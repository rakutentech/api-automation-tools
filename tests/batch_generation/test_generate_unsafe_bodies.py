import pytest

import apiautomationtools.batch_generation.batch_generation as bg

pytestmark = pytest.mark.batch_generation


def test_generate_unsafe_bodies_sub_value():
    body = {"field1": "value1", "field2": "2", "file": "file", "file2": "file2"}
    unsafe_bodies = bg.generate_unsafe_bodies(body)
    expected_bodies = [
        {"field1": "value1  '--", "field2": "2  '--"},
        {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {"field1": "value1  '--", "field2": "2  '--"},
        {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
        {"field1": "value1  '--", "field2": "2  '--"},
        {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
        {"field1": "value1  '--", "field2": "2  '--"},
        {
            "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
        },
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {"field1": "value1  '--", "field2": "2  '--"},
        {
            "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
        },
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
        {"field1": "value1  '--", "field2": "2  '--"},
        {
            "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
        },
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
        {"field1": "value1  '--", "field2": "2  '--"},
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
        {"field1": "value1 '+OR+1=1--", "field2": "2 '+OR+1=1--"},
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
        {
            "field1": "value1 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
            "field2": "2 ' and substr(version(),1,10) = 'PostgreSQL' and '1  -> OK",
        },
        {"field1": "value1 SELECT version() --", "field2": "2 SELECT version() --"},
        {
            "field1": "value1 select database_to_xml(true,true,'');",
            "field2": "2 select database_to_xml(true,true,'');",
        },
        {
            "field1": "value1 UNION SELECT * FROM information_schema.tables --",
            "field2": "2 UNION SELECT * FROM information_schema.tables --",
        },
    ]
    assert unsafe_bodies == expected_bodies
