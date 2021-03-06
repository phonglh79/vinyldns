import pytest
from utils import *
from hamcrest import *
from vinyldns_python import VinylDNSClient
from test_data import TestData
from dns.resolver import *


def test_create_recordset_with_dns_verify(shared_zone_test_context):
    """
    Test creating a new record set in an existing zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': 'test_create_recordset_with_dns_verify',
            'type': 'A',
            'ttl': 100,
            'records': [
                {
                    'address': '10.1.1.1'
                },
                {
                    'address': '10.2.2.2'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

        records = [x['address'] for x in result_rs['records']]
        assert_that(records, has_length(2))
        assert_that('10.1.1.1', is_in(records))
        assert_that('10.2.2.2', is_in(records))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        answers = dns_resolve(shared_zone_test_context.ok_zone, result_rs['name'], result_rs['type'])
        rdata_strings = rdata(answers)

        assert_that(answers, has_length(2))
        assert_that('10.1.1.1', is_in(rdata_strings))
        assert_that('10.2.2.2', is_in(rdata_strings))
    finally:
        if result_rs:
            try:
                delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
                client.wait_until_recordset_change_status(delete_result, 'Complete')
            except:
                pass


def test_create_srv_recordset_with_service_and_protocol(shared_zone_test_context):
    """
    Test creating a new srv record set with service and protocol works
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': '_sip._tcp._test-create-srv-ok',
            'type': 'SRV',
            'ttl': 100,
            'records': [
                {
                    'priority': 1,
                    'weight': 2,
                    'port': 8000,
                    'target': 'srv.'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_srv_recordset_with_service_and_protocol(shared_zone_test_context):
    """
    Test creating a new srv record set with service and protocol works
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': '_sip._tcp._test-create-srv-ok',
            'type': 'SRV',
            'ttl': 100,
            'records': [
                {
                    'priority': 1,
                    'weight': 2,
                    'port': 8000,
                    'target': 'srv.'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_aaaa_recordset_with_shorthand_record(shared_zone_test_context):
    """
    Test creating an AAAA record using shorthand for record data works
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': 'testAAAA',
            'type': 'AAAA',
            'ttl': 100,
            'records': [
                {
                    'address': '1::2'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_aaaa_recordset_with_normal_record(shared_zone_test_context):
    """
    Test creating an AAAA record not using shorthand for record data works
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': 'testAAAA',
            'type': 'AAAA',
            'ttl': 100,
            'records': [
                {
                    'address': '1:2:3:4:5:6:7:8'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_recordset_conflict(shared_zone_test_context):
    """
    Test creating a record set with the same name and type of an existing one returns a 409
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': 'test_create_recordset_conflict',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    result = None
    result_rs = None

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        client.create_recordset(result_rs, status=409)
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_recordset_conflict_with_case_insensitive_name(shared_zone_test_context):
    """
    Test creating a record set with the same name, but different casing, and type of an existing one returns a 409
    """
    client = shared_zone_test_context.ok_vinyldns_client
    first_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': 'test_create_recordset_conflict',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    result = None
    result_rs = None

    try:
        result = client.create_recordset(first_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        first_rs['name'] = 'test_create_recordset_CONFLICT'
        client.create_recordset(first_rs, status=409)
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_recordset_conflict_with_trailing_dot_insensitive_name(shared_zone_test_context):
    """
    Test creating a record set with the same name (but without a trailing dot) and type of an existing one returns a 409
    """
    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    first_rs = {
        'zoneId': zone['id'],
        'name': 'parent.com.',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    result_rs = None
    try:
        result = client.create_recordset(first_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        first_rs['name'] = 'parent.com'
        client.create_recordset(first_rs, status=409)

    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_recordset_conflict_with_dns(shared_zone_test_context):
    """
     Test creating a duplicate record set with the same name and same type of an existing one in DNS fails
     """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': 'backend-conflict',
        'type': 'A',
        'ttl': 38400,
        'records': [
            {
                'address': '7.7.7.7'    #records with different data should fail, these live in the dns hosts
            }
        ]
    }

    try:
        dns_add(shared_zone_test_context.ok_zone, "backend-conflict", 200, "A", "1.2.3.4")
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print json.dumps(result, indent=3)
        client.wait_until_recordset_change_status(result, 'Failed')

    finally:
        dns_delete(shared_zone_test_context.ok_zone, "backend-conflict", "A")


def test_create_recordset_conflict_with_dns_different_type(shared_zone_test_context):
    """
    Test creating a new record set in a zone with the same name as an existing record
    but with a different record type succeeds
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None
    try:
        new_rs = {
            'zoneId': shared_zone_test_context.ok_zone['id'],
            'name': 'already-exists',
            'type': 'TXT',
            'ttl': 100,
            'records': [
                {
                    'text': 'should succeed'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(shared_zone_test_context.ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

        text = [x['text'] for x in result_rs['records']]
        assert_that(text, has_length(1))
        assert_that('should succeed', is_in(text))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        answers = dns_resolve(shared_zone_test_context.ok_zone, result_rs['name'], result_rs['type'])
        rdata_strings = rdata(answers)
        assert_that(rdata_strings, has_length(1))
        assert_that('"should succeed"', is_in(rdata_strings))

    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_recordset_zone_not_found(shared_zone_test_context):
    """
    Test creating a new record set in a zone that doesn't exist should return a 404
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': '1234',
        'name': 'test_create_recordset_zone_not_found',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    client.create_recordset(new_rs, status=404)


def test_create_missing_record_data(shared_zone_test_context):
    """
    Test that creating a record without providing necessary data returns errors
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = dict({"no": "data"}, zoneId=shared_zone_test_context.system_test_zone['id'])

    errors = client.create_recordset(new_rs, status=400)['errors']
    assert_that(errors, contains_inanyorder(
        "Missing RecordSet.name",
        "Missing RecordSet.type",
        "Missing RecordSet.ttl"
    ))


def test_create_invalid_record_type(shared_zone_test_context):
    """
    Test that creating a record with invalid data returns errors
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'test_create_invalid_record_type',
        'type': 'invalid type',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }

    errors = client.create_recordset(new_rs, status=400)['errors']
    assert_that(errors, contains_inanyorder("Invalid RecordType"))


def test_create_invalid_record_data(shared_zone_test_context):
    """
    Test that creating a record with invalid data returns errors
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'test_create_invalid_record.data',
        'type': 'A',
        'ttl': 5,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': 'not.ipv4'
            },
            {  # Currently, list validation is fail-fast, so the "Missing A.address" that should happen here never does
                'nonsense': 'gibberish'
            }
        ]
    }

    errors = client.create_recordset(new_rs, status=400)['errors']

    import json

    print json.dumps(errors, indent=4)
    assert_that(errors, contains_inanyorder(
        "A must be a valid IPv4 Address",
        "RecordSet.ttl must be a positive signed 32 bit number greater than or equal to 30"
    ))

def test_create_dotted_a_record_not_apex_fails(shared_zone_test_context):
    """
    Test that creating a dotted host name A record set fails.
    """

    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    dotted_host_a_record = {
        'zoneId': zone['id'],
        'name': 'hello.world',
        'type': 'A',
        'ttl': 500,
        'records': [{'address': '127.0.0.1'}]
    }

    error = client.create_recordset(dotted_host_a_record, status=422)
    assert_that(error, is_("Record with name " + dotted_host_a_record['name'] + " is a dotted host which "
                              "is illegal in this zone " + zone['name']))

def test_create_dotted_a_record_apex_succeeds(shared_zone_test_context):
    """
    Test that creating an apex A record set containing dots succeeds.
    """

    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    apex_a_record = {
        'zoneId': zone['id'],
        'name': zone['name'].rstrip('.'),
        'type': 'A',
        'ttl': 500,
        'records': [{'address': '127.0.0.1'}]
    }
    apex_a_rs = None
    try:
        apex_a_response = client.create_recordset(apex_a_record, status=202)
        apex_a_rs = client.wait_until_recordset_change_status(apex_a_response, 'Complete')['recordSet']
        assert_that(apex_a_rs['name'],is_(apex_a_record['name'] + '.'))

    finally:
        if apex_a_rs:
            delete_result = client.delete_recordset(apex_a_rs['zoneId'], apex_a_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')

def test_create_dotted_a_record_apex_with_trailing_dot_succeeds(shared_zone_test_context):
    """
    Test that creating an apex A record set containing dots succeeds (with trailing dot)
    """

    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    apex_a_record = {
        'zoneId': zone['id'],
        'name': zone['name'],
        'type': 'A',
        'ttl': 500,
        'records': [{'address': '127.0.0.1'}]
    }
    apex_a_rs = None
    try:
        apex_a_response = client.create_recordset(apex_a_record, status=202)
        apex_a_rs = client.wait_until_recordset_change_status(apex_a_response, 'Complete')['recordSet']
        assert_that(apex_a_rs['name'],is_(apex_a_record['name']))

    finally:
        if apex_a_rs:
            delete_result = client.delete_recordset(apex_a_rs['zoneId'], apex_a_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')

def test_create_dotted_cname_record_apex_fails(shared_zone_test_context):
    """
    Test that creating a CNAME record set with record name matching dotted apex returns an error.
    """
    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    apex_cname_rs = {
        'zoneId': zone['id'],
        'name': zone['name'].rstrip('.'),
        'type': 'CNAME',
        'ttl': 500,
        'records': [{'cname': 'foo'}]
    }

    errors = client.create_recordset(apex_cname_rs, status=400)['errors']
    assert_that(errors[0], is_("Record name cannot contain '.' with given type"))

def test_create_cname_with_multiple_records(shared_zone_test_context):
    """
    Test that creating a CNAME record set with multiple records returns an error
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'test_create_cname_with_multiple_records',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'cname1.com'
            },
            {
                'cname': 'cname2.com'
            }
        ]
    }

    errors = client.create_recordset(new_rs, status=400)['errors']
    assert_that(errors[0], is_("CNAME record sets cannot contain multiple records"))


def test_create_cname_pointing_to_origin_symbol_fails(shared_zone_test_context):
    """
    Test that creating a CNAME record set with name '@' fails
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': '@',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'cname.'
            }
        ]
    }

    error = client.create_recordset(new_rs, status=422)
    assert_that(error, is_("CNAME RecordSet cannot have name '@' because it points to zone origin"))


def test_create_cname_with_existing_record_with_name_fails(shared_zone_test_context):
    """
    Test that creating a CNAME fails if a record with the same name exists
    """
    client = shared_zone_test_context.ok_vinyldns_client

    a_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'duplicate-test-name',
        'type': 'A',
        'ttl': 500,
        'records': [
            {
                'address': '10.1.1.1'
            }
        ]
    }

    cname_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'duplicate-test-name',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'cname1.com'
            }
        ]
    }

    try:
        a_create = client.create_recordset(a_rs, status=202)
        a_record = client.wait_until_recordset_change_status(a_create, 'Complete')['recordSet']

        error = client.create_recordset(cname_rs, status=409)
        assert_that(error, is_('RecordSet with name duplicate-test-name already exists in zone system-test., CNAME record cannot use duplicate name'))

    finally:
        delete_result = client.delete_recordset(a_record['zoneId'], a_record['id'], status=202)
        client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_record_with_existing_cname_fails(shared_zone_test_context):
    """
    Test that creating a record fails if a cname with the same name exists
    """
    client = shared_zone_test_context.ok_vinyldns_client

    cname_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'duplicate-test-name',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'cname1.com'
            }
        ]
    }

    a_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'duplicate-test-name',
        'type': 'A',
        'ttl': 500,
        'records': [
            {
                'address': '10.1.1.1'
            }
        ]
    }

    try:
        cname_create = client.create_recordset(cname_rs, status=202)
        cname_record = client.wait_until_recordset_change_status(cname_create, 'Complete')['recordSet']

        error = client.create_recordset(a_rs, status=409)
        assert_that(error, is_('RecordSet with name duplicate-test-name and type CNAME already exists in zone system-test.'))

    finally:
        delete_result = client.delete_recordset(cname_record['zoneId'], cname_record['id'], status=202)
        client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_cname_forces_record_to_be_absolute(shared_zone_test_context):
    """
    Test that CNAME record data is made absolute after being created
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'test_create_cname_with_multiple_records',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'cname1.com'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'cname' : 'cname1.com.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_cname_relative_fails(shared_zone_test_context):
    """
    Test that relative (no dots) CNAME record data fails
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'test_create_cname_relative',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'relative'
            }
        ]
    }

    client.create_recordset(new_rs, status=400)


def test_create_cname_does_not_change_absolute_record(shared_zone_test_context):
    """
    Test that CNAME record data that's already absolute is not changed after being created
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'test_create_cname_with_multiple_records',
        'type': 'CNAME',
        'ttl': 500,
        'records': [
            {
                'cname': 'cname1.'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'cname' : 'cname1.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_mx_forces_record_to_be_absolute(shared_zone_test_context):
    """
    Test that MX exchange is made absolute after being created
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'mx_not_absolute',
        'type': 'MX',
        'ttl': 500,
        'records': [
            {
                'preference': 1,
                'exchange': 'foo'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'preference' : 1, 'exchange' : 'foo.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_mx_does_not_change_if_absolute(shared_zone_test_context):
    """
    Test that MX exchange is unchanged if already absolute
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'mx_absolute',
        'type': 'MX',
        'ttl': 500,
        'records': [
            {
                'preference': 1,
                'exchange': 'foo.'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'preference' : 1, 'exchange' : 'foo.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_ptr_forces_record_to_be_absolute(shared_zone_test_context):
    """
    Test that ptr record data is made absolute after being created
    """
    client = shared_zone_test_context.ok_vinyldns_client
    reverse4_zone = shared_zone_test_context.ip4_reverse_zone

    new_rs = {
        'zoneId': reverse4_zone['id'],
        'name': '30.30',
        'type': 'PTR',
        'ttl': 500,
        'records': [
            {
                'ptrdname': 'foo'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'ptrdname' : 'foo.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_ptr_does_not_change_if_absolute(shared_zone_test_context):
    """
    Test that ptr record data is unchanged if already absolute
    """
    client = shared_zone_test_context.ok_vinyldns_client
    reverse4_zone = shared_zone_test_context.ip4_reverse_zone

    new_rs = {
        'zoneId': reverse4_zone['id'],
        'name': '30.30',
        'type': 'PTR',
        'ttl': 500,
        'records': [
            {
                'ptrdname': 'foo.'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'ptrdname' : 'foo.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_srv_forces_record_to_be_absolute(shared_zone_test_context):
    """
    Test that srv target is made absolute after being created
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'srv_not_absolute',
        'type': 'SRV',
        'ttl': 500,
        'records': [
            {
                'priority': 1,
                'weight': 1,
                'port': 1,
                'target': 'foo'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'priority' : 1, 'weight' : 1, 'port' : 1, 'target' : 'foo.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_srv_does_not_change_if_absolute(shared_zone_test_context):
    """
    Test that srv target is unchanged if already absolute
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'srv_absolute',
        'type': 'SRV',
        'ttl': 500,
        'records': [
            {
                'priority': 1,
                'weight': 1,
                'port': 1,
                'target': 'foo.'
            }
        ]
    }

    try:
        result = client.create_recordset(new_rs, status=202)
        result_rs = result['recordSet']
        assert_that(result_rs['records'], is_([{'priority' : 1, 'weight' : 1, 'port' : 1, 'target' : 'foo.'}]))
    finally:
        if result_rs:
            result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


@pytest.mark.parametrize('record_name,test_rs', TestData.FORWARD_RECORDS)
def test_create_recordset_forward_record_types(shared_zone_test_context, record_name, test_rs):
    """
    Test creating a new record set in an existing zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None

    try:
        new_rs = dict(test_rs, zoneId=shared_zone_test_context.system_test_zone['id'])

        result = client.create_recordset(new_rs, status=202)
        assert_that(result['status'], is_('Pending'))
        print str(result)

        result_rs = result['recordSet']
        verify_recordset(result_rs, new_rs)

        records = result_rs['records']

        for record in new_rs['records']:
            assert_that(records, has_item(has_entries(record)))

        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
    finally:
        if result_rs:
            result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=(202, 404))
            if result:
                client.wait_until_recordset_change_status(result, 'Complete')


@pytest.mark.parametrize('record_name,test_rs', TestData.REVERSE_RECORDS)
def test_reverse_create_recordset_reverse_record_types(shared_zone_test_context, record_name, test_rs):
    """
    Test creating a new record set in an existing reverse zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    result_rs = None

    try:
        new_rs = dict(test_rs, zoneId=shared_zone_test_context.ip4_reverse_zone['id'])

        result = client.create_recordset(new_rs, status=202)
        assert_that(result['status'], is_('Pending'))
        print str(result)

        result_rs = result['recordSet']
        verify_recordset(result_rs, new_rs)

        records = result_rs['records']

        for record in new_rs['records']:
            assert_that(records, has_item(has_entries(record)))

        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
    finally:
        if result_rs:
            result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=(202, 404))
            if result:
                client.wait_until_recordset_change_status(result, 'Complete')


def test_create_invalid_recordset_name(shared_zone_test_context):
    """
    Test creating a record set where the name is too long
    """
    client = shared_zone_test_context.ok_vinyldns_client

    new_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'a'*256,
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            }
        ]
    }
    client.create_recordset(new_rs, status=400)


def test_user_cannot_create_record_in_unowned_zone(shared_zone_test_context):
    """
    Test user can create a record that it a shared zone that it is a member of
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_record_set = {
        'zoneId': shared_zone_test_context.dummy_zone['id'],
        'name': 'test_user_cannot_create_record_in_unowned_zone',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.10.10.10'
            }
        ]
    }
    client.create_recordset(new_record_set, status=403)


def test_create_recordset_no_authorization(shared_zone_test_context):
    """
    Test creating a new record set without authorization
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': 'test_create_recordset_no_authorization',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    client.create_recordset(new_rs, sign_request=False, status=401)


def test_create_ipv4_ptr_recordset_with_verify(shared_zone_test_context):
    """
    Test creating a new IPv4 PTR recordset in an existing IPv4 reverse lookup zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    reverse4_zone = shared_zone_test_context.ip4_reverse_zone
    result_rs = None
    try:
        new_rs = {
            'zoneId': reverse4_zone['id'],
            'name': '30.0',
            'type': 'PTR',
            'ttl': 100,
            'records': [
                {
                    'ptrdname': 'ftp.vinyldns.'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(reverse4_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

        records = result_rs['records']
        assert_that(records[0]['ptrdname'], is_('ftp.vinyldns.'))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        # verify that the record exists in the backend dns server
        answers = dns_resolve(reverse4_zone, result_rs['name'], result_rs['type'])
        rdata_strings = rdata(answers)

        assert_that(answers, has_length(1))
        assert_that(rdata_strings[0], is_('ftp.vinyldns.'))
    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')



def test_create_ipv4_ptr_recordset_in_forward_zone_fails(shared_zone_test_context):
    """
    Test creating a new IPv4 PTR record set in an existing forward lookup zone fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': '35.0',
        'type': 'PTR',
        'ttl': 100,
        'records': [
            {
                'ptrdname': 'ftp.vinyldns.'
            }
        ]
    }
    client.create_recordset(new_rs, status=422)


def test_create_address_recordset_in_ipv4_reverse_zone_fails(shared_zone_test_context):
    """
    Test creating an A recordset in an existing IPv4 reverse lookup zone fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ip4_reverse_zone['id'],
        'name': 'test_create_address_recordset_in_ipv4_reverse_zone_fails',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '10.1.1.1'
            },
            {
                'address': '10.2.2.2'
            }
        ]
    }
    client.create_recordset(new_rs, status=422)


def test_create_ipv6_ptr_recordset(shared_zone_test_context):
    """
    Test creating a new PTR record set in an existing IPv6 reverse lookup zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    reverse6_zone = shared_zone_test_context.ip6_reverse_zone
    result_rs = None
    try:
        new_rs = {
            'zoneId': reverse6_zone['id'],
            'name': '0.6.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0',
            'type': 'PTR',
            'ttl': 100,
            'records': [
                {
                    'ptrdname': 'ftp.vinyldns.'
                }
            ]
        }
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

        records = result_rs['records']
        assert_that(records[0]['ptrdname'], is_('ftp.vinyldns.'))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        answers = dns_resolve(reverse6_zone, result_rs['name'], result_rs['type'])
        rdata_strings = rdata(answers)
        assert_that(answers, has_length(1))
        assert_that(rdata_strings[0], is_('ftp.vinyldns.'))
    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_ipv6_ptr_recordset_in_forward_zone_fails(shared_zone_test_context):
    """
    Test creating a new PTR record set in an existing forward lookup zone fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': '3.6.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0',
        'type': 'PTR',
        'ttl': 100,
        'records': [
            {
                'ptrdname': 'ftp.vinyldns.'
            }
        ]
    }
    client.create_recordset(new_rs, status=422)


def test_create_address_recordset_in_ipv6_reverse_zone_fails(shared_zone_test_context):
    """
    Test creating a new A record set in an existing IPv6 reverse lookup zone fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ip6_reverse_zone['id'],
        'name': 'test_create_address_recordset_in_ipv6_reverse_zone_fails',
        'type': 'AAAA',
        'ttl': 100,
        'records': [
            {
                'address': 'fd69:27cc:fe91::60'
            },
            {
                'address': 'fd69:27cc:fe91:1:2:3:4:61'
            }
        ]
    }
    client.create_recordset(new_rs, status=422)


def test_create_invalid_ipv6_ptr_recordset(shared_zone_test_context):
    """
    Test creating an incorrect IPv6 PTR record in an existing IPv6 reverse lookup zone fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ip6_reverse_zone['id'],
        'name': '0.6.0.0',
        'type': 'PTR',
        'ttl': 100,
        'records': [
            {
                'ptrdname': 'ftp.vinyldns.'
            }
        ]
    }
    client.create_recordset(new_rs, status=422)


def test_at_create_recordset(shared_zone_test_context):
    """
    Test creating a new record set with name @ in an existing zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    ok_zone = shared_zone_test_context.ok_zone
    result_rs = None
    try:
        new_rs = {
            'zoneId': ok_zone['id'],
            'name': '@',
            'type': 'TXT',
            'ttl': 100,
            'records': [
                {
                    'text': 'someText'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)

        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        expected_rs = new_rs
        expected_rs['name'] = ok_zone['name']
        verify_recordset(result_rs, expected_rs)

        print "\r\n\r\n!!!recordset verified..."

        records = result_rs['records']
        assert_that(records, has_length(1))
        assert_that(records[0]['text'], is_('someText'))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        # verify that the record exists in the backend dns server
        answers = dns_resolve(ok_zone, ok_zone['name'], result_rs['type'])

        rdata_strings = rdata(answers)
        assert_that(rdata_strings, has_length(1))
        assert_that('"someText"', is_in(rdata_strings))
    finally:
        if result_rs:
            client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=(202, 404))
            client.wait_until_recordset_deleted(result_rs['zoneId'], result_rs['id'])

def test_create_record_with_escape_characters_in_record_data_succeeds(shared_zone_test_context):
    """
    Test creating a new record set with escape characters (i.e. "" and \) in the record data
    """
    client = shared_zone_test_context.ok_vinyldns_client
    ok_zone = shared_zone_test_context.ok_zone
    result_rs = None
    try:
        new_rs = {
            'zoneId': ok_zone['id'],
            'name': 'testing',
            'type': 'TXT',
            'ttl': 100,
            'records': [
                {
                    'text': 'escaped\char"act"ers'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(ok_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)

        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        expected_rs = new_rs
        expected_rs['name'] = 'testing'
        verify_recordset(result_rs, expected_rs)

        print "\r\n\r\n!!!recordset verified..."

        records = result_rs['records']
        assert_that(records, has_length(1))
        assert_that(records[0]['text'], is_('escaped\\char\"act\"ers'))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        # verify that the record exists in the backend dns server
        answers = dns_resolve(ok_zone, 'testing', result_rs['type'])

        rdata_strings = rdata(answers)
        assert_that(rdata_strings, has_length(1))
        assert_that('\"escapedchar\\"act\\"ers\"', is_in(rdata_strings))
    finally:
        if result_rs:
            client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=(202, 404))
            client.wait_until_recordset_deleted(result_rs['zoneId'], result_rs['id'])



def test_create_record_with_existing_wildcard_succeeds(shared_zone_test_context):
    """
    Test that creating a record when a wildcard record of the same type already exists succeeds
    """
    client = shared_zone_test_context.ok_vinyldns_client

    wildcard_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': '*',
        'type': 'TXT',
        'ttl': 500,
        'records': [
            {
                'text': 'wildcard func test 1'
            }
        ]
    }

    test_rs = {
        'zoneId': shared_zone_test_context.system_test_zone['id'],
        'name': 'create-record-with-existing-wildcard-succeeds',
        'type': 'TXT',
        'ttl': 500,
        'records': [
            {
                'text': 'wildcard this should be ok'
            }
        ]
    }

    try:
        wildcard_create = client.create_recordset(wildcard_rs, status=202)
        wildcard_rs = client.wait_until_recordset_change_status(wildcard_create, 'Complete')['recordSet']

        test_create = client.create_recordset(test_rs, status=202)
        test_rs = client.wait_until_recordset_change_status(test_create, 'Complete')['recordSet']
    finally:
        try:
            delete_result = client.delete_recordset(wildcard_rs['zoneId'], wildcard_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')
        finally:
            try:
                delete_result = client.delete_recordset(test_rs['zoneId'], test_rs['id'], status=202)
                client.wait_until_recordset_change_status(delete_result, 'Complete')
            except:
                pass


def test_create_record_with_existing_cname_wildcard_succeed(shared_zone_test_context):
    """
    Test that creating a record when a CNAME wildcard record already exists succeeds
    """
    client = shared_zone_test_context.ok_vinyldns_client

    zone = shared_zone_test_context.system_test_zone

    wildcard_rs = get_recordset_json(zone, '*', 'CNAME', [{'cname': 'cname2.'}])

    test_rs = get_recordset_json(zone, 'new_record', 'A', [{'address': '10.1.1.1'}])

    try:
        wildcard_create = client.create_recordset(wildcard_rs, status=202)
        wildcard_rs = client.wait_until_recordset_change_status(wildcard_create, 'Complete')['recordSet']

        test_create = client.create_recordset(test_rs, status=202)
        test_rs = client.wait_until_recordset_change_status(test_create, 'Complete')['recordSet']
    finally:
        try:
            delete_result = client.delete_recordset(wildcard_rs['zoneId'], wildcard_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')
        finally:
            try:
                delete_result = client.delete_recordset(test_rs['zoneId'], test_rs['id'], status=202)
                client.wait_until_recordset_change_status(delete_result, 'Complete')
            except:
                pass


def test_dotted_host_create_fails(shared_zone_test_context):
    """
    Tests that a dotted host recordset create fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    new_rs = {
        'zoneId': shared_zone_test_context.ok_zone['id'],
        'name': 'record-with.dot',
        'type': 'TXT',
        'ttl': 100,
        'records': [
            {
                'text': 'should fail'
            }
        ]
    }
    error = client.create_recordset(new_rs, status=422)
    assert_that(error, is_('Record with name record-with.dot is a dotted host which is illegal in this zone ok.'))


def test_ns_create_for_admin_group_succeeds(shared_zone_test_context):
    """
    Tests that an ns change passes
    """
    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone
    result_rs = None

    try:
        new_rs = {
            'zoneId': zone['id'],
            'name': 'someNS',
            'type': 'NS',
            'ttl': 38400,
            'records': [
                {
                    'nsdname': 'ns1.parent.com.'
                }
            ]
        }
        result = client.create_recordset(new_rs, status=202)
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']

    finally:
        if result_rs:
            client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=(202,404))
            client.wait_until_recordset_deleted(result_rs['zoneId'], result_rs['id'])


def test_ns_create_for_unapproved_server_fails(shared_zone_test_context):
    """
    Tests that an ns change fails if one of the servers isnt approved
    """
    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    new_rs = {
        'zoneId': zone['id'],
        'name': 'someNS',
        'type': 'NS',
        'ttl': 38400,
        'records': [
            {
                'nsdname': 'ns1.parent.com.'
            },
            {
                'nsdname': 'this.is.bad.'
            }
        ]
    }
    client.create_recordset(new_rs, status=422)


def test_ns_create_for_origin_fails(shared_zone_test_context):
    """
    Tests that an ns create for origin fails
    """
    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.parent_zone

    new_rs = {
        'zoneId': zone['id'],
        'name': '@',
        'type': 'NS',
        'ttl': 38400,
        'records': [
            {
                'nsdname': 'ns1.parent.com.'
            }
        ]
    }
    client.create_recordset(new_rs, status=409)


def test_create_ipv4_ptr_recordset_with_verify_in_classless(shared_zone_test_context):
    """
    Test creating a new IPv4 PTR record set in an existing IPv4 classless delegation zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    reverse4_zone = shared_zone_test_context.classless_zone_delegation_zone
    result_rs = None

    try:
        new_rs = {
            'zoneId': reverse4_zone['id'],
            'name': '196',
            'type': 'PTR',
            'ttl': 100,
            'records': [
                {
                    'ptrdname': 'ftp.vinyldns.'
                }
            ]
        }
        print "\r\nCreating recordset in zone " + str(reverse4_zone) + "\r\n"
        result = client.create_recordset(new_rs, status=202)
        print str(result)

        assert_that(result['changeType'], is_('Create'))
        assert_that(result['status'], is_('Pending'))
        assert_that(result['created'], is_not(none()))
        assert_that(result['userId'], is_not(none()))

        result_rs = result['recordSet']
        result_rs = client.wait_until_recordset_change_status(result, 'Complete')['recordSet']
        print "\r\n\r\n!!!recordset is active!  Verifying..."

        verify_recordset(result_rs, new_rs)
        print "\r\n\r\n!!!recordset verified..."

        records = result_rs['records']
        assert_that(records[0]['ptrdname'], is_('ftp.vinyldns.'))

        print "\r\n\r\n!!!verifying recordset in dns backend"
        # verify that the record exists in the backend dns server
        answers = dns_resolve(reverse4_zone, result_rs['name'], result_rs['type'])
        rdata_strings = rdata(answers)

        assert_that(answers, has_length(1))
        assert_that(rdata_strings[0], is_('ftp.vinyldns.'))
    finally:
        if result_rs:
            delete_result = client.delete_recordset(result_rs['zoneId'], result_rs['id'], status=202)
            client.wait_until_recordset_change_status(delete_result, 'Complete')


def test_create_ipv4_ptr_recordset_in_classless_outside_cidr(shared_zone_test_context):
    """
    Test new IPv4 PTR recordset fails outside the cidr range for a IPv4 classless delegation zone
    """
    client = shared_zone_test_context.ok_vinyldns_client
    reverse4_zone = shared_zone_test_context.classless_zone_delegation_zone

    new_rs = {
        'zoneId': reverse4_zone['id'],
        'name': '190',
        'type': 'PTR',
        'ttl': 100,
        'records': [
            {
                'ptrdname': 'ftp.vinyldns.'
            }
        ]
    }

    error = client.create_recordset(new_rs, status=422)
    assert_that(error, is_('RecordSet 190 does not specify a valid IP address in zone 192/30.2.0.192.in-addr.arpa.'))


def test_create_high_value_domain_fails(shared_zone_test_context):
    """
    Test that creating a record configured as a High Value Domain fails
    """

    client = shared_zone_test_context.ok_vinyldns_client
    zone = shared_zone_test_context.ok_zone
    new_rs = {
        'zoneId': zone['id'],
        'name': 'high-value-domain',
        'type': 'A',
        'ttl': 100,
        'records': [
            {
                'address': '1.1.1.1'
            }
        ]
    }

    error = client.create_recordset(new_rs, status=422)
    assert_that(error, is_('Record name "high-value-domain.ok." is configured as a High Value Domain, so it cannot be modified.'))


def test_create_high_value_domain_fails_for_ip4_ptr(shared_zone_test_context):
    """
    Test that creating a record configured as a High Value Domain fails for ip4 ptr record
    """

    client = shared_zone_test_context.ok_vinyldns_client
    ptr = {
        'zoneId': shared_zone_test_context.classless_base_zone['id'],
        'name': '252',
        'type': 'PTR',
        'ttl': 100,
        'records': [
            {
                'ptrdname': 'test.foo.'
            }
        ]
    }

    error_ptr = client.create_recordset(ptr, status=422)
    assert_that(error_ptr, is_('Record name "192.0.2.252" is configured as a High Value Domain, so it cannot be modified.'))


def test_create_high_value_domain_fails_for_ip6_ptr(shared_zone_test_context):
    """
    Test that creating a record configured as a High Value Domain fails for ip6 ptr record
    """

    client = shared_zone_test_context.ok_vinyldns_client
    ptr = {
        'zoneId': shared_zone_test_context.ip6_reverse_zone['id'],
        'name': 'f.f.f.f.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0',
        'type': 'PTR',
        'ttl': 100,
        'records': [
            {
                'ptrdname': 'test.foo.'
            }
        ]
    }

    error_ptr = client.create_recordset(ptr, status=422)
    assert_that(error_ptr, is_('Record name "fd69:27cc:fe91:0000:0000:0000:0000:ffff" is configured as a High Value Domain, so it cannot be modified.'))
