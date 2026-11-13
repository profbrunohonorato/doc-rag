import pytest
from Application.helpers.chunk_helper import split_text


def test_ingestion_updates_deletes_and_deduplicates(stack):
    settings, services = stack
    path = settings.documents_path / 'conta.txt'
    path.write_text('Para abrir conta apresente CPF.', encoding='utf-8')
    first = services.ingestion.scan()[0]
    assert first['status'] == 'indexed'
    calls = services.ai.calls
    services.ingestion.scan()
    assert services.ai.calls == calls
    path.write_text('Para abrir conta apresente CPF e RG.', encoding='utf-8')
    second = services.ingestion.scan()[0]
    assert second['checksum'] != first['checksum']
    assert services.vectors.collection.count() == 1
    assert 'RG' in services.vectors.search([1., 0., 0.], 4)[0]['text']
    path.unlink()
    assert services.ingestion.scan()[0]['status'] == 'removed'
    assert services.vectors.collection.count() == 0


def test_failures_do_not_leave_stale_content_and_retry(stack):
    settings, services = stack
    path = settings.documents_path / 'conta.txt'
    path.write_text('CPF para conta')
    services.ingestion.scan()
    path.write_text('CPF novo para conta')
    services.ai.fail = True
    assert services.ingestion.scan()[0]['status'] == 'error'
    assert services.vectors.collection.count() == 0
    services.ai.fail = False
    assert services.ingestion.scan()[0]['status'] == 'indexed'


def test_model_change_reindexes(stack):
    settings, services = stack
    (settings.documents_path / 'conta.txt').write_text('CPF para conta')
    first = services.ingestion.scan()[0]
    settings.embedding_model = 'another-model'
    assert services.ingestion.scan()[0]['checksum'] != first['checksum']


def test_grounded_answer_review_and_audit(stack):
    settings, services = stack
    (settings.documents_path / 'conta.md').write_text('Para abrir conta apresente CPF e identificação.')
    services.ingestion.scan()
    answer = services.rag.ask('Como abrir conta?')
    assert answer['status'] == 'pending'
    assert answer['sources'][0]['name'] == 'conta.md'
    approved = services.repository.review(answer['id'], 'approved', 'Pesquisador', 'Fonte conferida')
    assert approved['status'] == 'approved'
    with pytest.raises(ValueError):
        services.repository.review(answer['id'], 'rejected', 'Outro', '')
    events = services.repository.audit()
    assert events[0]['details']['reviewer'] == 'Pesquisador'
    assert len(services.repository.answers()) == 1


def test_abstains_on_missing_evidence_and_invalid_citations(stack):
    settings, services = stack
    assert services.rag.ask('Abrir conta?')['status'] == 'insufficient_evidence'
    (settings.documents_path / 'conta.txt').write_text('CPF para conta')
    services.ingestion.scan()
    assert services.rag.ask('Explique astronomia')['status'] == 'insufficient_evidence'
    services.ai.response = 'Resposta inventada [99]'
    assert services.rag.ask('Abrir conta?')['status'] == 'insufficient_evidence'


def test_chunking_preserves_text_and_validates():
    text = 'abcdefghijklmnopqrstuvwxyz'
    chunks = split_text(text, 10, 2)
    assert chunks[0] + ''.join(c[2:] for c in chunks[1:]) == text
    with pytest.raises(ValueError):
        split_text(text, 10, 10)


def test_symlink_and_oversized_files(stack, tmp_path):
    settings, services = stack
    outside = tmp_path / 'secret.txt'
    outside.write_text('secret')
    (settings.documents_path / 'link.txt').symlink_to(outside)
    assert services.ingestion.scan() == []
    settings.max_file_bytes = 5
    (settings.documents_path / 'large.txt').write_text('too large')
    assert services.ingestion.scan()[0]['status'] == 'error'
