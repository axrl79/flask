import os
from flask import Blueprint, request, jsonify, send_file, current_app
from src.services.document_service import DocumentService
from src.core.exceptions import ValidationException, DocumentNotFoundException

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")
doc_service = DocumentService()


@documents_bp.route("/upload", methods=["POST"])
def upload_document():
    """
    POST /api/documents/upload
    Recibe un manual técnico PDF mediante multipart/form-data.
    """
    if "file" not in request.files:
        raise ValidationException("El campo 'file' es requerido en el formulario multipart.")

    file = request.files["file"]
    document = doc_service.upload_document(file)
    return jsonify(document.to_dict()), 201


@documents_bp.route("", methods=["GET"])
def list_documents():
    """
    GET /api/documents
    Lista todos los documentos con filtros opcionales de status y search.
    """
    status = request.args.get("status")
    search = request.args.get("search")
    documents = doc_service.list_documents(status=status, search=search)
    return jsonify([doc.to_dict() for doc in documents]), 200


@documents_bp.route("/<document_id>", methods=["GET"])
def get_document(document_id):
    """
    GET /api/documents/<document_id>
    Retorna el detalle completo y estado de un documento.
    """
    document = doc_service.get_document(document_id)
    return jsonify(document.to_dict()), 200


@documents_bp.route("/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    """
    DELETE /api/documents/<document_id>
    Elimina un documento y su archivo físico asociado.
    """
    doc_service.delete_document(document_id)
    return jsonify({"message": f"Documento {document_id} eliminado exitosamente."}), 200


@documents_bp.route("/<document_id>/download", methods=["GET"])
def download_document(document_id):
    """
    GET /api/documents/<document_id>/download
    Descarga o visualiza de forma segura el archivo PDF original.
    """
    document = doc_service.get_document(document_id)
    if not os.path.exists(document.file_path):
        raise DocumentNotFoundException("El archivo físico no se encuentra en el servidor.")

    return send_file(
        document.file_path,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=document.original_filename,
    )


@documents_bp.route("/<document_id>/index", methods=["POST"])
def index_document(document_id):
    """
    POST /api/documents/<document_id>/index
    Registra la solicitud de indexación del documento.
    """
    job = doc_service.trigger_indexing(document_id)
    return jsonify(job.to_dict()), 202
