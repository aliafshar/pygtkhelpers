
import py
import gtk, gtk.gdk
from pygtkhelpers.ui.objectlist import ObjectList, Column, Cell
from pygtkhelpers.utils import refresh_gui
from pygtkhelpers.test import CheckCalled
from mock import Mock
from .conftest import User


def test_append(items, user):
    assert len(items) == 0
    items.append(user)
    assert len(items) == 1
    assert items[0] is user
    assert user in items

    #containment is identity based
    assert User(name="hans", age=10) not in items

    #dont allow the same object twice
    py.test.raises(ValueError, items.append, user)

def test_append_selected(items, user):
    items.append(user, select=True)

    assert items.selected_item is user

def test_append_unselected(items, user):
    items.append(user, select=False)
    assert items.selected_item is None

def test_select_single_fails_when_select_multiple_is_set(items, user):
    items.append(user)
    items.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
    py.test.raises(AttributeError, 'items.selected_item = user')
    py.test.raises(AttributeError, 'items.selected_item')
    items.selected_items = [user]
    refresh_gui()
    assert items.selected_items == [user]

def test_extend(items):
    items.extend([
        User('hans', 22),
        User('peter', 22),
        ])
    assert len(items)==2

def test_remove(items, user):
    items.append(user)
    assert user in items
    items.remove(user)
    assert user not in items

def test_deselect(items, user):
    items.append(user)
    items.selected_item = user
    refresh_gui()
    items.selected_item = None
    refresh_gui()

def test_deselect_multiple(items, user, user2):
    listing = [user, user2]
    items.extend(listing)
    items.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
    items.selected_items = listing
    refresh_gui()
    assert items.selected_items == listing
    items.selected_items = []
    refresh_gui()
    assert items.selected_items == []

    items.selected_items = listing
    refresh_gui()
    assert items.selected_items == listing
    items.selected_items = None
    refresh_gui()
    assert items.selected_items == []

def test_remove_missing(items, user):
    py.test.raises(ValueError, items.remove, user)

def test_column_title():
    col = Column("name")
    view_col = col.create_treecolumn(None)
    assert view_col.get_title() == "Name"

    title_col = Column(title="Test", cells=[])
    title_view_col = title_col.create_treecolumn(None)
    assert title_view_col.get_title() == 'Test'
    assert len(title_view_col.get_cells()) == 0

def test_column_visiblility():
    col = Column('test')
    view_col = col.create_treecolumn(None)
    assert view_col.get_visible()

def test_column_invisiblility():
    col = Column('test', visible=False)
    view_col = col.create_treecolumn(None)
    assert not view_col.get_visible()

def test_column_width():
    col = Column('test', width=30)
    view_col = col.create_treecolumn(None)
    refresh_gui()
    assert view_col.get_sizing() == gtk.TREE_VIEW_COLUMN_FIXED
    assert view_col.get_fixed_width() == 30

def test_column_expandable():
    col = Column('name', expand=True)
    treeview_column = col.create_treecolumn(None)
    assert treeview_column.props.expand

def test_build_simple():
    uidef = '''
        <interface>
          <object class="PyGTKHelpersObjectList" id="test">
          </object>
        </interface>
    '''
    b = gtk.Builder()
    b.add_from_string(uidef)
    objectlist = b.get_object('test')
    print objectlist
    assert isinstance(objectlist, ObjectList)

def test_edit_name(items, user):
    items.append(user)
    item_changed = CheckCalled(items, 'item-changed')

    refresh_gui()
    assert not item_changed.called
    name_cell = items.get_columns()[0].get_cells()[0]
    text_path = items._path_for(user)
    name_cell.emit('edited', text_path, 'peter')
    refresh_gui()
    assert user.name=='peter'
    assert item_changed.called

def test_selection_changed_signal(items, user):
    items.append(user)
    selection_changed = CheckCalled(items, 'selection-changed')
    items.selected_item = user
    assert selection_changed.called

def test_left_click_event(items, user):
    items.append(user, select=True)
    e = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
    e.button = 1
    e.x, e.y = 10.0, 10.0
    item_clicked = CheckCalled(items, 'item-left-clicked')
    items._emit_for_path((0,), e)
    refresh_gui()
    assert item_clicked.called
    assert item_clicked.called_count == 1

def test_right_click_event(items, user):
    items.append(user, select=True)
    e = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
    e.button = 3
    item_clicked = CheckCalled(items, 'item-right-clicked')
    items._emit_for_path((0,), e)
    refresh_gui()
    assert item_clicked.called
    assert item_clicked.called_count == 1

def test_middle_click_event(items, user):
    items.append(user, select=True)
    e = gtk.gdk.Event(gtk.gdk.BUTTON_PRESS)
    e.button = 2
    item_clicked = CheckCalled(items, 'item-middle-clicked')
    items._emit_for_path((0,), e)
    refresh_gui()
    assert item_clicked.called
    assert item_clicked.called_count == 1

def test_double_click_event(items, user):
    items.append(user, select=True)
    e = gtk.gdk.Event(gtk.gdk._2BUTTON_PRESS)
    e.button = 1
    item_clicked = CheckCalled(items, 'item-double-clicked')
    items._emit_for_path((0,), e)
    refresh_gui()
    assert item_clicked.called
    assert item_clicked.called_count == 1

@py.test.mark.tree_only
def test_tree_expander_column(items):
    assert items.get_expander_column() is items.get_columns()[-1]

@py.test.mark.list_only
def test_list_expander_column(items):
    assert items.get_expander_column() is None

@py.test.mark.tree_only
def test_expanded_signal(items, user, user2):
    items.append(user)
    items.append(user2, user)
    item_expanded = CheckCalled(items, 'item-expanded')
    items.expand_row(items._path_for(user), True)
    refresh_gui()
    assert item_expanded.called

@py.test.mark.tree_only
def test_expand_item(items, user, user2):
    items.append(user)
    items.append(user2, user)
    item_expanded = CheckCalled(items, 'item-expanded')
    items.expand_item(user)
    refresh_gui()
    assert item_expanded.called

@py.test.mark.tree_only
def test_tree_collapse_item(items, user, user2):
    items.append(user)
    items.append(user2, user)
    item_collapsed = CheckCalled(items, 'item-collapsed')
    items.expand_item(user)
    refresh_gui()
    items.collapse_row(items._path_for(user))
    refresh_gui()
    assert item_collapsed.called

@py.test.mark.tree_only
def test_list_collapse_item(items, user, user2):
    items.append(user)
    items.append(user2, user)
    item_collapsed = CheckCalled(items, 'item-collapsed')
    items.expand_item(user)
    refresh_gui()
    items.collapse_item(user)
    refresh_gui()
    assert item_collapsed.called

@py.test.mark.tree_only
def test_item_expanded(items, user, user2):
    items.append(user)
    items.append(user2, user)
    items.expand_item(user)
    refresh_gui()
    assert items.item_expanded(user)
    items.collapse_item(user)
    refresh_gui()
    assert not items.item_expanded(user)

def test_move_item_up(items, user, user2):
    items.append(user)
    items.append(user2)
    items.move_item_up(user2)
    assert items._object_at_iter(0) is user2
    assert items._object_at_iter(1) is user

def test_move_item_down(items, user, user2):
    items.append(user)
    items.append(user2)
    items.move_item_down(user)
    assert items._object_at_iter(0) is user2
    assert items._object_at_iter(1) is user

def test_move_first_item_up(items, user, user2):
    items.append(user)
    items.append(user2)
    items.move_item_up(user)
    assert items._object_at_iter(0) is user
    assert items._object_at_iter(1) is user2

def test_move_last_item_down(items, user, user2):
    items.append(user)
    items.append(user2)
    items.move_item_down(user2)
    assert items._object_at_iter(0) is user
    assert items._object_at_iter(1) is user2

@py.test.mark.tree_only
def test_move_subitem_down(items, user, user2, user3):
    items.append(user)
    items.append(user2, parent=user)
    items.append(user3, parent=user)
    items.move_item_down(user2)
    assert (items._path_for(user2) ==
            items._path_for_iter(items._next_iter_for(user3)))

@py.test.mark.tree_only
def test_move_last_subitem_down(items, user, user2, user3):
    items.append(user)
    items.append(user2, parent=user)
    items.append(user3, parent=user)
    items.move_item_down(user3)
    assert (items._path_for(user3) ==
            items._path_for_iter(items._next_iter_for(user2)))

@py.test.mark.tree_only
def test_move_subitem_up(items, user, user2, user3):
    items.append(user)
    items.append(user2, parent=user)
    items.append(user3, parent=user)
    items.move_item_up(user3)
    assert (items._path_for(user2) ==
            items._path_for_iter(items._next_iter_for(user3)))

@py.test.mark.tree_only
def test_move_last_subitem_up(items, user, user2, user3):
    items.append(user)
    items.append(user2, parent=user)
    items.append(user3, parent=user)
    items.move_item_up(user2)
    assert (items._path_for(user3) ==
            items._path_for_iter(items._next_iter_for(user2)))

def test_view_iters(items, user, user2, user3):
    items.extend([user, user2, user3])
    items.set_visible_func(lambda obj: obj.age<100)
    refresh_gui()
    assert items.item_visible(user)
    assert not items.item_visible(user3)

def test_sort_by_attr_default(items):
    items.sort_by('name')
    assert items.model_sort.has_default_sort_func()

def test_sort_by_attr_asc(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items[0] is user
    assert items[1] is user2
    assert items[2] is user3
    items.sort_by('name')
    it = [i[0] for i in items.model_sort]
    assert it[0] is user2
    assert it[1] is user
    assert it[2] is user3

def test_sort_by_attr_desc(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items[0] is user
    assert items[1] is user2
    assert items[2] is user3
    items.sort_by('name', direction='desc')
    it = [i[0] for i in items.model_sort]
    assert it[0] is user3
    assert it[1] is user
    assert it[2] is user2

def _sort_key(obj):
    # key on the last letter of the name
    return obj.name[-1]

def test_sort_by_key_asc(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items[0] is user
    assert items[1] is user2
    assert items[2] is user3
    items.sort_by(_sort_key)
    it = [i[0] for i in items.model_sort]
    assert it[0] is user3
    assert it[1] is user2
    assert it[2] is user

def test_sort_by_key_desc(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items[0] is user
    assert items[1] is user2
    assert items[2] is user3
    items.sort_by(_sort_key, '-')
    it = [i[0] for i in items.model_sort]
    assert it[0] is user
    assert it[1] is user2
    assert it[2] is user3

def test_sort_by_col(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items[0] is user
    assert items[1] is user2
    assert items[2] is user3
    # simulate a click on the header
    items.model_sort.set_sort_column_id(0, gtk.SORT_ASCENDING)
    it = [i[0] for i in items.model_sort]
    assert it[0] is user2
    assert it[1] is user
    assert it[2] is user3

def test_sort_by_col_desc(items, user, user2, user3):
    items.extend([user, user2, user3])
    it = [i[0] for i in items.model_sort]
    assert it[0] is user
    assert it[1] is user2
    assert it[2] is user3
    ui = items._sort_iter_for(user)
    print items.model_sort.iter_next(ui)
    # simulate a click on the header
    items.model_sort.set_sort_column_id(0, gtk.SORT_DESCENDING)
    it = [i[0] for i in items.model_sort]
    assert it[0] is user3
    assert it[1] is user
    assert it[2] is user2

def test_sort_item_activated(items, user, user2, user3):
    items.extend([user, user2, user3])
    mock = Mock()
    items.connect('item-activated', mock.cb)
    items.emit('row-activated', '0', gtk.TreeViewColumn())
    assert mock.cb.call_args[0][1] is user

    items.sort_by('age', '-')
    items.emit('row-activated', '0', gtk.TreeViewColumn())
    assert mock.cb.call_args[0][1] is user3

def test_search_col(searchcheck):
    searchcheck.assert_selects('a', searchcheck.u1)

def test_search_col_insensitive(searchcheck):
    searchcheck.assert_selects('A', searchcheck.u1)

def test_search_col_missing(searchcheck):
    searchcheck.assert_selects('z', None)

def test_search_col_last(searchcheck):
    searchcheck.assert_selects('c', searchcheck.u3)

def test_search_attr(searchcheck):
    searchcheck.ol.search_by('age')
    searchcheck.assert_selects('1', searchcheck.u1)

def test_search_attr_missing(searchcheck):
    searchcheck.ol.search_by('age')
    searchcheck.assert_selects('z', None)

def _search_func(item, key):
    return item.age == 1

def test_search_func(searchcheck):
    searchcheck.ol.search_by(_search_func)
    searchcheck.assert_selects('z', searchcheck.u1)

def _search_missing_func(item, key):
    return item.age == 9

def test_search_missing_func(searchcheck):
    searchcheck.ol.search_by(_search_missing_func)
    searchcheck.assert_selects('z', None)

def test_item_after(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items.item_after(user) is user2
    assert items.item_after(user2) is user3
    assert items.item_after(user3) is None

def test_item_before(items, user, user2, user3):
    items.extend([user, user2, user3])
    assert items.item_before(user2) is user
    assert items.item_before(user3) is user2
    assert items.item_before(user) is None

