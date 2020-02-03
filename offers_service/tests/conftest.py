import pytest
import http.client
from offers.app import create_app
from .constants import PRIVATE_KEY
from offers import token_validation
from faker import Faker
fake = Faker()


@pytest.fixture
def app():
    application = create_app()

    application.app_context().push()
    # Initialise the DB
    application.db.create_all()

    return application


@pytest.fixture
def offer_fixture(client):
    '''
    Generate three offers in the system.
    '''

    offer_ids = []
    for _ in range(3):
        offer = {
            'title': fake.text(150),
            'description': fake.text(250),
            'category': fake.text(20),
            'latitude': fake.latitude(),
            'longitude': fake.longitude(),
            'picture_url': fake.text(150),
        }
        header = token_validation.generate_token_header(fake.name(),
                                                        PRIVATE_KEY)
        headers = {
            'Authorization': header,
        }
        response = client.post('/api/me/offers/', data=offer,
                               headers=headers)
        assert http.client.CREATED == response.status_code
        result = response.json
        offer_ids.append(result['id'])

    yield offer_ids

    # Clean up all offers
    response = client.get('/api/offers/')
    offers = response.json
    for offer in offers:
        offer_id = offer['id']
        url = f'/admin/offers/{offer_id}/'
        response = client.delete(url)
        assert http.client.NO_CONTENT == response.status_code
