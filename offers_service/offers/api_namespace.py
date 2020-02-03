import http.client
from datetime import datetime
from flask_restplus import Namespace, Resource, fields
from offers import config
from offers.models import OfferModel
from offers.token_validation import validate_token_header
from offers.db import db
from flask import abort

api_namespace = Namespace('api', description='API operations')


def authentication_header_parser(value):
    username = validate_token_header(value, config.PUBLIC_KEY)
    if username is None:
        abort(401)
    return username


# Input and output formats for offer

authentication_parser = api_namespace.parser()
authentication_parser.add_argument('Authorization', location='headers',
                                   type=str,
                                   help='Bearer Access Token')

offer_parser = authentication_parser.copy()
offer_parser.add_argument('title', type=str, required=True,
                          help='Title of the offer')
offer_parser.add_argument('description', type=str, required=True,
                          help='Description of the offer')
offer_parser.add_argument('category', type=str, required=True,
                          help='Offer Category')
offer_parser.add_argument('latitude', type=float,
                          help='Location(latitude) of the offer')
offer_parser.add_argument('longitude', type=float,
                          help='Location(longitude) of the offer')
offer_parser.add_argument('picture_url', type=str,
                          help='Picture of the offer')
model = {
    'id': fields.Integer(),
    'title': fields.String(),
    'username': fields.String(),
    'description': fields.String(),
    'category': fields.String(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'picture_url': fields.String(),
    'timestamp': fields.DateTime(),
}
offer_model = api_namespace.model('Offer', model)


@api_namespace.route('/me/offers/')
class MeOfferListCreate(Resource):

    @api_namespace.doc('list_offers')
    @api_namespace.expect(authentication_parser)
    @api_namespace.marshal_with(offer_model, as_list=True)
    def get(self):
        '''
        Retrieves all the offers
        '''
        args = authentication_parser.parse_args()
        username = authentication_header_parser(args['Authorization'])

        offers = (OfferModel
                  .query
                  .filter(OfferModel.username == username)
                  .order_by('id')
                  .all())
        return offers

    @api_namespace.doc('create_offer')
    @api_namespace.expect(offer_parser)
    @api_namespace.marshal_with(offer_model, code=http.client.CREATED)
    def post(self):
        '''
        Create a new offer
        '''
        args = offer_parser.parse_args()
        username = authentication_header_parser(args['Authorization'])

        new_offer = OfferModel(username=username,
                               title=args['title'],
                               description=args['description'],
                               category=args['category'],
                               latitude=args['latitude'],
                               longitude=args['longitude'],
                               picture_url=args['picture_url'],
                               timestamp=datetime.utcnow())
        db.session.add(new_offer)
        db.session.commit()

        result = api_namespace.marshal(new_offer, offer_model)

        return result, http.client.CREATED


search_parser = api_namespace.parser()
search_parser.add_argument('search', type=str, required=False,
                           help='Search in the description of the offers')


@api_namespace.route('/offers/')
class OfferList(Resource):

    @api_namespace.doc('list_offers')
    @api_namespace.marshal_with(offer_model, as_list=True)
    @api_namespace.expect(search_parser)
    def get(self):
        '''
        Retrieves all the offers
        '''
        args = search_parser.parse_args()
        search_param = args['search']
        query = OfferModel.query
        if search_param:
            query = (query.filter(OfferModel.description.contains(search_param)))

        query = query.order_by('id')
        offers = query.all()

        return offers


@api_namespace.route('/offers/<int:offer_id>/')
class OffersRetrieve(Resource):

    @api_namespace.doc('retrieve_offer')
    @api_namespace.marshal_with(offer_model)
    def get(self, offer_id):
        '''
        Retrieve a offer
        '''
        offer = OfferModel.query.get(offer_id)
        if not offer:
            # The offer is not present
            return '', http.client.NOT_FOUND

        return offer
