'''
Test the Offers operations


Use the offer_fixture to have data to retrieve, it generates three offers
'''
from unittest.mock import ANY
import http.client
from freezegun import freeze_time
from .constants import PRIVATE_KEY
from offers import token_validation
from faker import Faker
fake = Faker()


@freeze_time('2019-05-07 13:47:34')
def test_create_me_offer(client):
    new_offer = {
        'username': fake.name(),
        'title': fake.text(150),
        'description': fake.text(240),
        'category': fake.text(50),
        'latitude': fake.latitude(),
        'longitude': fake.longitude(),
        'picture_url': fake.text(150),
    }
    header = token_validation.generate_token_header(fake.name(),
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }
    response = client.post('/api/me/offers/', data=new_offer,
                           headers=headers)
    result = response.json

    assert http.client.CREATED == response.status_code

    expected = {
        'id': ANY,
        'username': ANY,
        'title': new_offer['title'],
        'description': new_offer['description'],
        'category': new_offer['category'],
        'latitude': ANY,
        'longitude': ANY,
        'picture_url': new_offer['picture_url'],
        'timestamp': '2019-05-07T13:47:34',
    }
    assert result == expected


def test_create_me_unauthorized(client):
    new_offer = {
        'username': fake.name(),
        'title': fake.text(150),
        'description': fake.text(240),
        'category': fake.text(50),
        'latitude': fake.latitude(),
        'longitude': fake.longitude(),
        'picture_url': fake.text(150),
    }
    response = client.post('/api/me/offers/', data=new_offer)
    assert http.client.UNAUTHORIZED == response.status_code


def test_list_me_offers(client, offer_fixture):
    username = fake.name()
    title = fake.text(150)
    description = fake.text(240)
    category = fake.text(50)
    latitude = fake.latitude()
    longitude = fake.longitude()
    picture_url = fake.text(150)

    # Create a new offer
    new_offer = {
        'title': title,
        'description': description,
        'category': category,
        'latitude': latitude,
        'longitude': longitude,
        'picture_url': picture_url,
    }
    header = token_validation.generate_token_header(username,
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }
    response = client.post('/api/me/offers/', data=new_offer,
                           headers=headers)
    result = response.json

    assert http.client.CREATED == response.status_code

    # Get the offers of the user
    response = client.get('/api/me/offers/', headers=headers)
    results = response.json

    assert http.client.OK == response.status_code
    assert len(results) == 1
    result = results[0]
    expected_result = {
        'id': ANY,
        'username': username,
        'title': title,
        'description': description,
        'category': category,
        'picture_url': picture_url,
        'latitude': ANY,
        'longitude': ANY,
        'timestamp': ANY,
    }

    assert result == expected_result


def test_list_me_unauthorized(client):
    response = client.get('/api/me/offers/')
    assert http.client.UNAUTHORIZED == response.status_code


def test_list_offers(client, offer_fixture):
    response = client.get('/api/offers/')
    result = response.json

    assert http.client.OK == response.status_code
    assert len(result) > 0

    # Check that the ids are increasing
    previous_id = -1
    for offer in result:
        expected = {
            'description': ANY,
            'title': ANY,
            'username': ANY,
            'id': ANY,
            'category': ANY,
            'latitude': ANY,
            'longitude': ANY,
            'picture_url': ANY,
            'timestamp': ANY,
        }
        assert expected == offer
        assert offer['id'] > previous_id
        previous_id = offer['id']


def test_list_offers_search(client, offer_fixture):
    username = fake.name()
    new_offer = {
        'username': username,
        'title': 'A tale',
        'description': 'A tale about a Platypus',
        'category': 'Home',
        'latitude': 0,
        'longitude': 0,
        'picture_url': 'localhost',
    }
    header = token_validation.generate_token_header(username,
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }
    response = client.post('/api/me/offers/', data=new_offer,
                           headers=headers)
    assert http.client.CREATED == response.status_code

    response = client.get('/api/offers/?search=platypus')
    result = response.json

    assert http.client.OK == response.status_code
    assert len(result) > 0

    # Check that the returned values contain "platypus"
    for offer in result:
        expected = {
            'description': ANY,
            'title': ANY,
            'username': username,
            'id': ANY,
            'category': ANY,
            'latitude': ANY,
            'longitude': ANY,
            'picture_url': ANY,
            'timestamp': ANY,
        }
        assert expected == offer
        assert 'platypus' in offer['description'].lower()


def test_get_offer(client, offer_fixture):
    offer_id = offer_fixture[0]
    response = client.get(f'/api/offers/{offer_id}/')
    result = response.json

    assert http.client.OK == response.status_code
    assert 'title' in result
    assert 'description' in result
    assert 'category' in result
    assert 'picture_url' in result
    assert 'username' in result
    assert 'timestamp' in result
    assert 'id' in result


def test_get_non_existing_offer(client, offer_fixture):
    offer_id = 123456
    response = client.get(f'/api/offers/{offer_id}/')

    assert http.client.NOT_FOUND == response.status_code
