import http.client
from flask_restplus import Namespace, Resource
from offers.models import OfferModel
from offers.db import db

admin_namespace = Namespace('admin', description='Admin operations')


@admin_namespace.route('/offers/<int:offer_id>/')
class OffersDelete(Resource):

    @admin_namespace.doc('delete_offer',
                         responses={http.client.NO_CONTENT: 'No content'})
    def delete(self, offer_id):
        '''
        Delete a offer
        '''
        offer = OfferModel.query.get(offer_id)
        if not offer:
            # The offer is not present
            return '', http.client.NO_CONTENT

        db.session.delete(offer)
        db.session.commit()

        return '', http.client.NO_CONTENT
