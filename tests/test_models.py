import pytest
from db_init import db_create
from db_models import db, Case, Item
from app import app

db_create()


@pytest.fixture(scope="module")
def new_case():
    with app.app_context():
        case = Case(name="Test Case", image_path="test_image.jpg", user_id=1)
        db.session.add(case)
        db.session.commit()
        yield case
        db.session.delete(case)
        db.session.commit()


def test_create_case(new_case):
    assert new_case.name == "Test Case"
    assert new_case.image_path == "test_image.jpg"
    assert new_case.user_id == 1


def test_read_case(new_case):
    readed_case = Case.query.get(new_case.id)
    assert readed_case is not None


def test_update_case(new_case):
    new_case.name = "Updated Test Case"
    new_case.image_path = "updated_image.jpg"
    db.session.commit()

    updated_case = Case.query.get(new_case.id)
    assert updated_case is not None
    assert updated_case.name == "Updated Test Case"
    assert updated_case.image_path == "updated_image.jpg"


def test_delete_case(new_case):
    db.session.delete(new_case)
    db.session.commit()

    deleted_case = Case.query.get(new_case.id)
    assert deleted_case is None


@pytest.fixture(scope="module")
def new_item():
    with app.app_context():
        item = Item(name="Test Item", image_path="test_item_image.jpg", case_id=1, user_id=1)
        db.session.add(item)
        db.session.commit()
        yield item
        db.session.delete(item)
        db.session.commit()


def test_create_item(new_item):
    assert new_item.name == "Test Item"
    assert new_item.image_path == "test_item_image.jpg"
    assert new_item.case_id == 1
    assert new_item.user_id == 1


def test_read_item(new_item):
    readed_item = Item.query.get(new_item.id)
    assert readed_item is not None


def test_update_item(new_item):
    new_item.name = "Updated Test Case"
    new_item.image_path = "updated_image.jpg"
    db.session.commit()

    updated_item = Item.query.get(new_item.id)
    assert updated_item is not None
    assert updated_item.name == "Updated Test Case"
    assert updated_item.image_path == "updated_image.jpg"


def test_delete_item(new_item):
    db.session.delete(new_item)
    db.session.commit()

    deleted_item = Item.query.get(new_item.id)
    assert deleted_item is None
