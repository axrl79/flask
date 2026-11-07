import io
import json
import os
import time
from src import create_app
from src.extensions import db
from tests.create_sample_pdf import create_sample_industrial_manual

app = create_app("development")
client = app.test_client()

print("=" * 70)
print("INICIANDO PRUEBAS DE INTEGRACIÓN END-TO-END DEL MOTOR RAG")
print("=" * 70)

with app.app_context():
    # 1. Crear PDF de prueba
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "manual_prueba_ga37.pdf")
    create_sample_industrial_manual(pdf_path)

    # 2. Subida del documento
    print("\n[1] Subiendo manual técnico PDF...")
    with open(pdf_path, "rb") as f:
        upload_resp = client.post(
            "/api/documents/upload",
            data={"file": (f, "Manual_Compresor_GA37_Industrial.pdf")},
            content_type="multipart/form-data",
        )
    assert upload_resp.status_code == 201, f"Error en upload: {upload_resp.data}"
    doc_data = upload_resp.get_json()
    doc_id = doc_data["id"]
    print(f"-> Documento subido con ID: {doc_id}, páginas: {doc_data['total_pages']}, hash: {doc_data.get('file_hash_sha256', '')[:8]}...")

    # 3. Verificación de rechazo de duplicados
    print("\n[2] Probando prevención de duplicados (SHA-256)...")
    with open(pdf_path, "rb") as f:
        dup_resp = client.post(
            "/api/documents/upload",
            data={"file": (f, "Manual_Copia.pdf")},
            content_type="multipart/form-data",
        )
    assert dup_resp.status_code == 409, f"Se esperaba 409 en duplicado, se obtuvo: {dup_resp.status_code}"
    print("-> Documento duplicado correctamente rechazado con código 409 DOCUMENT_DUPLICATE.")

    # 4. Disparar indexación RAG con embeddings reales
    print("\n[3] Ejecutando indexación completa en ChromaDB (PyMuPDF + nomic-embed-text)...")
    idx_resp = client.post(f"/api/documents/{doc_id}/index")
    assert idx_resp.status_code == 202, f"Error en indexación: {idx_resp.data}"
    job_data = idx_resp.get_json()
    print(f"-> Indexación completada: chunks indexados: {job_data['total_chunks_indexed']}, etapa: {job_data['stage']}")

    # 5. Consulta 1: Código de Error
    print("\n[4] Consulta 1: Código de Error E-205...")
    q1 = "¿Qué significa el código E-205 y cuál es la solución indicada?"
    r1 = client.post("/api/chat/query", json={"query": q1, "document_id": doc_id})
    assert r1.status_code == 200
    res1 = r1.get_json()
    print(f"Pregunta: {q1}")
    print(f"Respuesta: {res1['answer']}")
    print(f"Fuentes ({len(res1['sources'])}): {[s['document_name'] + ' Pág.' + str(s['page_number']) for s in res1['sources']]}")
    print(f"Evidencia suficiente: {res1['evidence_sufficient']}, Latencia: {res1['latency_seconds']}s")

    # 6. Consulta 2: Especificaciones técnicas y torques
    print("\n[5] Consulta 2: Especificaciones técnicas y torques...")
    q2 = "¿Cuál es el torque de apriete para los pernos M12 del elemento compresor y cuál es la presión máxima de trabajo?"
    r2 = client.post("/api/chat/query", json={"query": q2, "document_id": doc_id})
    assert r2.status_code == 200
    res2 = r2.get_json()
    print(f"Pregunta: {q2}")
    print(f"Respuesta: {res2['answer']}")
    print(f"Fuentes ({len(res2['sources'])}): {[s['document_name'] + ' Pág.' + str(s['page_number']) for s in res2['sources']]}")

    # 7. Consulta 3: Procedimiento de arranque
    print("\n[6] Consulta 3: Procedimiento de arranque seguro...")
    q3 = "¿Cuáles son los pasos obligatorios para el arranque seguro del compresor GA-37?"
    r3 = client.post("/api/chat/query", json={"query": q3, "document_id": doc_id})
    assert r3.status_code == 200
    res3 = r3.get_json()
    print(f"Pregunta: {q3}")
    print(f"Respuesta: {res3['answer']}")

    # 8. Consulta 4: Pregunta cuya respuesta no existe en el manual (Prueba negativa anti-alucinación)
    print("\n[7] Consulta 4: Prueba negativa anti-alucinaciones...")
    q4 = "¿Cómo se calibra el sensor de oxígeno y cuál es la concentración de nitrógeno en el escape?"
    r4 = client.post("/api/chat/query", json={"query": q4, "document_id": doc_id})
    assert r4.status_code == 200
    res4 = r4.get_json()
    print(f"Pregunta: {q4}")
    print(f"Respuesta: {res4['answer']}")
    print(f"Evidencia suficiente reportada: {res4['evidence_sufficient']}")

    # 9. Consulta 5: Historial y estadísticas del Dashboard
    print("\n[8] Verificando métricas en /api/dashboard/stats...")
    stats_resp = client.get("/api/dashboard/stats")
    stats_data = stats_resp.get_json()
    print(f"-> Estadísticas: {json.dumps(stats_data, indent=2)}")

    print("\n" + "=" * 70)
    print("TODAS LAS PRUEBAS END-TO-END COMPLETADAS EXITOSAMENTE!")
    print("=" * 70)

    # Limpieza
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
