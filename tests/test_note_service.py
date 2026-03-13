import pytest


def test_add_get_update_delete_note(fake_note_repository):
    from assistant_bot.domain.exceptions import NoteNotFoundError
    from assistant_bot.services.note_service import NoteService

    svc = NoteService(fake_note_repository)

    note = svc.add_note("abc", tags=["t1"])
    assert note.content == "abc"

    got = svc.get_note(note.note_id)
    assert got.note_id == note.note_id

    svc.update_note(note.note_id, content="def", tags=["t2"])
    updated = svc.get_note(note.note_id)
    assert updated.content == "def"
    assert updated.tags == ["t2"]

    svc.delete_note(note.note_id)

    with pytest.raises(NoteNotFoundError):
        svc.get_note(note.note_id)


def test_search_and_sorting(fake_note_repository):
    from assistant_bot.services.note_service import NoteService

    svc = NoteService(fake_note_repository)

    note_1 = svc.add_note("first note", tags=["aa"])
    note_2 = svc.add_note("second note", tags=["bb", "cc"])

    by_tag = svc.get_notes_by_tag("aa")
    assert any(note.note_id == note_1.note_id for note in by_tag)

    by_any = svc.get_notes_by_any_tag(["bb", "x"])
    assert any(note.note_id == note_2.note_id for note in by_any)

    by_all = svc.get_notes_by_all_tags(["bb", "cc"])
    assert any(note.note_id == note_2.note_id for note in by_all)

    sorted_by_tags = svc.get_notes_sorted_by_tags()
    assert sorted_by_tags[0].note_id == note_2.note_id