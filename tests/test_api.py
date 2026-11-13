from fastapi.testclient import TestClient
from Presentation.API.main import app
from Presentation.API.settings import get_settings
from Infra.IoC.dependencies_helper import get_services


def test_api_auth_upload_question_review_and_validation(stack, monkeypatch):
    settings, services = stack
    settings.api_token = 'test-token'
    monkeypatch.setattr('Presentation.API.main.get_services', lambda: services)
    monkeypatch.setattr('Presentation.API.main.watch', idle_watch)
    # Lifespan cache cleanup belongs to the production factory.
    monkeypatch.setattr('Presentation.API.main.get_services', Factory(services))
    app.dependency_overrides[get_services] = lambda: services
    app.dependency_overrides[get_settings] = lambda: settings
    monkeypatch.setattr('Presentation.API.security.get_settings', lambda: settings)
    monkeypatch.setattr('Presentation.API.controllers.documents_controller.get_settings', lambda: settings)
    monkeypatch.setattr('Presentation.API.main.get_settings', lambda: settings)
    try:
        with TestClient(app) as client:
            assert client.get('/doc-rag/api/v1/health/live').status_code == 200
            assert client.get('/doc-rag/api/v1/documents').status_code == 401
            client.headers['Authorization'] = 'Bearer test-token'
            assert client.post('/doc-rag/api/v1/documents/upload', files={'file': ('../bad.txt', b'x')}).status_code == 400
            assert client.post('/doc-rag/api/v1/documents/upload', files={'file': ('a.exe', b'x')}).status_code == 415
            assert client.post('/doc-rag/api/v1/documents/upload', files={'file': ('a.txt', b'')}).status_code == 400
            settings.max_file_bytes = 5
            assert client.post('/doc-rag/api/v1/documents/upload', files={'file': ('a.txt', b'123456')}).status_code == 413
            settings.max_file_bytes = 10000
            assert client.post('/doc-rag/api/v1/documents/upload', files={'file': ('conta.txt', b'CPF para abrir conta')}).status_code == 201
            assert client.post('/doc-rag/api/v1/documents/scan').json()[0]['status'] == 'indexed'
            assert client.post('/doc-rag/api/v1/chat/ask', json={'question': '   '}).status_code == 422
            response = client.post('/doc-rag/api/v1/chat/ask', json={'question': 'Como abrir conta?'})
            assert response.status_code == 200
            answer_id = response.json()['id']
            response = client.post(f'/doc-rag/api/v1/answers/{answer_id}/review', json={'decision': 'approved', 'reviewer': 'Ana'})
            assert response.json()['status'] == 'approved'
            assert client.post('/doc-rag/api/v1/answers/missing/review', json={'decision': 'approved', 'reviewer': 'Ana'}).status_code == 404
            assert len(client.get('/doc-rag/api/v1/audit').json()) >= 3
    finally:
        app.dependency_overrides.clear()


class Factory:
    def __init__(self, services):
        self.services = services

    def __call__(self):
        return self.services

    def cache_clear(self):
        pass


async def idle_watch(services, stop):
    await stop.wait()
