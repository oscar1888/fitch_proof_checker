import pytest
from unittest.mock import MagicMock
from fitch_proof_checker.presenter.gm_presenter import GMPresenter


@pytest.fixture
def view():
    v = MagicMock()
    v.list_connectives = MagicMock()
    v.list_quantifiers = MagicMock()
    return v


@pytest.fixture
def model():
    m = MagicMock()

    conn = MagicMock()
    conn.name = "And"
    conn.symbol = "&"

    quant = MagicMock()
    quant.name = "For All"
    quant.symbol = "∀"

    m.grammar_manager.connectives = [conn]
    m.grammar_manager.quantifiers = [quant]

    return m


@pytest.fixture
def presenter(view, model):
    return GMPresenter(view, model)


def test_init(view, model):
    pres = GMPresenter(view, model)
    assert pres.model == model
    assert pres.view == view
    view.add_presenter.assert_called_once_with(pres)


def test_populate_list_connectives(presenter, view):
    presenter.populate_list('connective')

    view.list_connectives.clear.assert_called_once()
    view.list_connectives.addItem.assert_called_once_with("And (&)")
    view.list_quantifiers.clear.assert_not_called()


def test_populate_list_quantifiers(presenter, view):
    presenter.populate_list('quantifier')

    view.list_quantifiers.clear.assert_called_once()
    view.list_quantifiers.addItem.assert_called_once_with("For All (∀)")
    view.list_connectives.clear.assert_not_called()


def test_get_item_name(presenter):
    assert presenter.get_item_name('connective', 0) == "And"
    assert presenter.get_item_name('quantifier', 0) == "For All"


def test_is_protected_item(presenter, mocker):
    mock_fol_gm = MagicMock()

    prot_conn = MagicMock()
    prot_conn.name = "ProtectedAnd"
    mock_fol_gm.connectives = [prot_conn]
    mock_fol_gm.quantifiers = []

    mocker.patch(
        'fitch_proof_checker.presenter.gm_presenter.GrammarFactory.create_first_order_logic',
        return_value=mock_fol_gm
    )

    mocker.patch.object(presenter, 'get_item_name', return_value="ProtectedAnd")
    assert presenter.is_protected_item('connective', 0) is True

    mocker.patch.object(presenter, 'get_item_name', return_value="CustomXOR")
    assert presenter.is_protected_item('connective', 1) is False


def test_remove_item(presenter, mocker):
    mocker.patch.object(presenter, 'populate_list')

    initial_len = len(presenter.model.grammar_manager.connectives)

    presenter.remove_item('connective', 0)

    assert len(presenter.model.grammar_manager.connectives) == initial_len - 1
    presenter.populate_list.assert_called_once_with('connective')


def test_add_item_success_connective(presenter, tmp_path, mocker):
    mocker.patch.object(presenter, 'populate_list')

    plugin_file = tmp_path / "my_plugin.py"
    plugin_file.write_text("class CustomConnective:\n    name = 'XOR'\n")

    success, msg = presenter.add_item('connective', str(plugin_file))

    assert success is True
    assert "loaded successfully!" in msg
    assert len(presenter.model.grammar_manager.connectives) == 2
    presenter.populate_list.assert_called_once_with('connective')


def test_add_item_success_quantifier(presenter, tmp_path, mocker):
    mocker.patch.object(presenter, 'populate_list')

    plugin_file = tmp_path / "my_plugin.py"
    plugin_file.write_text("class CustomQuantifier:\n    name = 'ExistsAtLeastTwo'\n")

    success, msg = presenter.add_item('quantifier', str(plugin_file))

    assert success is True
    assert "loaded successfully!" in msg
    assert len(presenter.model.grammar_manager.quantifiers) == 2
    presenter.populate_list.assert_called_once_with('quantifier')


def test_add_item_missing_class(presenter, tmp_path):
    plugin_file = tmp_path / "bad_plugin.py"
    plugin_file.write_text("class WrongName:\n    pass\n")

    success, msg = presenter.add_item('connective', str(plugin_file))

    assert success is False
    assert "must contain a class named 'CustomConnective'" in msg


def test_add_item_quantifier():
    presenter = MagicMock()
    presenter.model.grammar_manager.quantifiers = []

    new_item = MagicMock()

    item_type = 'quantifier'
    if item_type == 'quantifier':
        presenter.model.grammar_manager.quantifiers.append(new_item)

    assert new_item in presenter.model.grammar_manager.quantifiers
    assert len(presenter.model.grammar_manager.quantifiers) == 1


def test_load_default_grammar(presenter, mocker):
    mock_pl = MagicMock()
    mock_fol = MagicMock()

    mocker.patch('fitch_proof_checker.presenter.gm_presenter.GrammarFactory.create_propositional_logic',
                 return_value=mock_pl)
    mocker.patch('fitch_proof_checker.presenter.gm_presenter.GrammarFactory.create_first_order_logic',
                 return_value=mock_fol)
    mocker.patch.object(presenter, 'populate_list')

    presenter.load_default_grammar("Propositional Logic (PL)")
    assert presenter.model.grammar_manager == mock_pl

    presenter.load_default_grammar("First-Order Logic (FOL)")
    assert presenter.model.grammar_manager == mock_fol

    assert presenter.populate_list.call_count == 4


def test_load_profile_success(presenter, mocker):
    mocker.patch.object(presenter, 'populate_list')

    success, msg = presenter.load_profile("dummy.json")

    assert success is True
    presenter.model.grammar_manager.load_vocabulary_from_json.assert_called_once_with("dummy.json")
    assert presenter.populate_list.call_count == 2


def test_load_profile_exception(presenter):
    presenter.model.grammar_manager.load_vocabulary_from_json.side_effect = Exception("File Error")

    success, msg = presenter.load_profile("dummy.json")

    assert success is False
    assert "File Error" in msg


def test_save_profile_success(presenter):
    success, msg = presenter.save_profile("out.json")

    assert success is True
    presenter.model.grammar_manager.save_vocabulary_to_json.assert_called_once_with("out.json")


def test_save_profile_exception(presenter):
    presenter.model.grammar_manager.save_vocabulary_to_json.side_effect = Exception("Write Error")

    success, msg = presenter.save_profile("out.json")

    assert success is False
    assert "Write Error" in msg


def test_add_item_exception_branch(presenter):
    success, error_msg = presenter.add_item('quantifier', 'fake_string_data')

    assert success is False
    assert "Failed to load quantifier" in error_msg
    assert "'NoneType' object has no attribute 'loader'" in error_msg
