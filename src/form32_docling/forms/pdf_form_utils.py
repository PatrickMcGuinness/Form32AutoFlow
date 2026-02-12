"""Shared PDF form generation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from pypdf import PdfReader, PdfWriter
from pypdf.constants import UserAccessPermissions
from pypdf.generic import BooleanObject, DictionaryObject, NameObject, NumberObject


@dataclass(frozen=True)
class EncryptionProfile:
    """Template encryption settings to preserve in generated output."""

    permissions_flag: UserAccessPermissions
    algorithm: str


def extract_encryption_profile(reader: PdfReader) -> EncryptionProfile | None:
    """Extract encryption settings from a template PDF reader."""
    if not reader.is_encrypted:
        return None

    reader.decrypt("")
    encrypt_dict = reader.trailer.get("/Encrypt")
    if encrypt_dict is None:
        return None

    encrypt_obj = encrypt_dict.get_object()
    template_permissions = int(encrypt_obj.get("/P", 0))
    permissions_flag = UserAccessPermissions(template_permissions)

    revision = int(encrypt_obj.get("/R", 0) or 0)
    if revision >= 6:
        algorithm = "AES-256"
    elif revision >= 4:
        algorithm = "AES-128"
    else:
        return None

    return EncryptionProfile(permissions_flag=permissions_flag, algorithm=algorithm)


def clone_template_to_writer(reader: PdfReader) -> PdfWriter:
    """Clone template content into a writer and preserve header version."""
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer.pdf_header = reader.pdf_header
    return writer


def apply_field_values(
    writer: PdfWriter,
    field_values: dict[str, Any],
    page_spec: int | None = None,
    *,
    auto_regenerate: bool | None = None,
) -> None:
    """Apply form field values to a writer."""
    target: Any = None if page_spec is None else writer.pages[page_spec]

    writer.update_page_form_field_values(
        target, field_values, auto_regenerate=auto_regenerate
    )


def normalize_for_acrobat(writer: PdfWriter) -> None:
    """Normalize output for Acrobat fill/edit behavior."""
    if "/Perms" in writer._root_object:
        del writer._root_object[NameObject("/Perms")]

    acro_ref = writer._root_object.get("/AcroForm")
    acro: DictionaryObject
    if acro_ref is None:
        acro = DictionaryObject()
        writer._root_object[NameObject("/AcroForm")] = acro
    else:
        acro = cast(DictionaryObject, acro_ref.get_object())

    acro[NameObject("/NeedAppearances")] = BooleanObject(True)
    if "/SigFlags" in acro:
        current_flags = int(acro.get("/SigFlags", 0) or 0)
        acro[NameObject("/SigFlags")] = NumberObject(current_flags & ~2)


def reencrypt_writer_if_needed(
    writer: PdfWriter, profile: EncryptionProfile | None
) -> None:
    """Re-encrypt writer output if template had encryption settings."""
    if profile is None:
        return
    writer.encrypt(
        "",
        permissions_flag=profile.permissions_flag,
        algorithm=profile.algorithm,
    )
