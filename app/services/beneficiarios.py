from app.models.beneficiarios import (
    Beneficiario, BeneficiarioAlergia, BeneficiarioPatologia,
    HistorialPatologia, MedicamentoBeneficiario, HistorialPrescripcion,
)
from app.models.historia_clinica import HistoriaClinica
from app.config.database import AsyncSessionLocal
from app.utils.exceptions import ValidationError
from sqlmodel import select
from datetime import datetime, date
from typing import Dict, Any, Optional

class ServicioBeneficiarios:
    
    @staticmethod
    async def registrar_auditoria(
        db, 
        beneficiario_id: int, 
        usuario_id: int, 
        tabla: str, 
        operacion: str,
        registro_id: Optional[int] = None,
        campo: Optional[str] = None,
        anterior: Optional[str] = None,
        nuevo: Optional[str] = None,
        motivo: Optional[str] = None
    ):
        """Helper para registrar cambios en la historia clínica"""
        auditoria = HistoriaClinica(
            beneficiario_id=beneficiario_id,
            modificado_por=usuario_id,
            tabla_modificada=tabla,
            registro_id=registro_id,
            campo_modificado=campo or "registro",
            valor_anterior=str(anterior) if anterior is not None else None,
            valor_nuevo=str(nuevo) if nuevo is not None else None,
            tipo_operacion=operacion,
            motivo=motivo
        )
        db.add(auditoria)

    @staticmethod
    async def crear_beneficiario(datos: Dict[str, Any], usuario_id: int) -> Beneficiario:
        async with AsyncSessionLocal() as db:
            # Validaciones básicas
            if not datos.get("identificacion") or not datos.get("nombres"):
                raise ValidationError("Identificación y nombres son obligatorios")
            
            # Verificar duplicados
            stmt = select(Beneficiario).where(Beneficiario.identificacion == datos["identificacion"])
            result = await db.execute(stmt)
            if result.scalar_one_or_none():
                raise ValidationError("Ya existe un beneficiario con esta identificación")

            nuevo = Beneficiario(**datos)
            db.add(nuevo)
            await db.flush() # Para obtener el ID

            # Registrar en historia clínica
            await ServicioBeneficiarios.registrar_auditoria(
                db, nuevo.id, usuario_id, "Beneficiario", "Creación", nuevo.id
            )

            await db.commit()
            await db.refresh(nuevo)
            return nuevo

    @staticmethod
    async def actualizar_beneficiario(beneficiario_id: int, datos: Dict[str, Any], usuario_id: int) -> Beneficiario:
        async with AsyncSessionLocal() as db:
            stmt = select(Beneficiario).where(Beneficiario.id == beneficiario_id)
            result = await db.execute(stmt)
            beneficiario = result.scalar_one_or_none()
            
            if not beneficiario:
                raise ValidationError("Beneficiario no encontrado")

            for campo, nuevo_valor in datos.items():
                valor_anterior = getattr(beneficiario, campo)
                if valor_anterior != nuevo_valor:
                    # Registrar cambio en historia clínica
                    await ServicioBeneficiarios.registrar_auditoria(
                        db, beneficiario_id, usuario_id, "Beneficiario", "Modificación", 
                        beneficiario_id, campo, valor_anterior, nuevo_valor
                    )
                    setattr(beneficiario, campo, nuevo_valor)

            beneficiario.updated_at = datetime.now()
            await db.commit()
            await db.refresh(beneficiario)
            return beneficiario

    @staticmethod
    async def asignar_medicamento(beneficiario_id: int, medicamento_id: int, datos: Dict[str, Any], usuario_id: int):
        async with AsyncSessionLocal() as db:
            # Si ya existe uno activo, lo cerramos o lanzamos error?
            # Aquí implementaremos la lógica de M:N
            asignacion = MedicamentoBeneficiario(
                beneficiario_id=beneficiario_id,
                medicamento_id=medicamento_id,
                **datos
            )
            db.add(asignacion)
            
            await ServicioBeneficiarios.registrar_auditoria(
                db, beneficiario_id, usuario_id, "MedicamentoBeneficiario", "Creación", 
                None, "asignacion_medicamento", None, f"ID Medicamento: {medicamento_id}"
            )
            
            await db.commit()
            return asignacion

    @staticmethod
    async def editar_prescripcion(asignacion_id: int, nuevos_datos: Dict[str, Any], usuario_id: int, motivo: str):
        async with AsyncSessionLocal() as db:
            stmt = select(MedicamentoBeneficiario).where(MedicamentoBeneficiario.id == asignacion_id)
            result = await db.execute(stmt)
            original = result.scalar_one_or_none()
            
            if not original:
                raise ValidationError("Prescripción no encontrada")

            # Mover registro antiguo al historial según requerimiento
            historial = HistorialPrescripcion(
                medicamento_beneficiario_id_original=original.id,
                beneficiario_id=original.beneficiario_id,
                medicamento_id=original.medicamento_id,
                dosis=original.dosis,
                frecuencia=original.frecuencia,
                fecha_inicio=original.fecha_inicio,
                fecha_fin=original.fecha_fin,
                activo=original.activo,
                motivo_cambio=motivo,
                modificado_por=usuario_id
            )
            db.add(historial)

            # Actualizar registro principal
            for campo, valor in nuevos_datos.items():
                setattr(original, campo, valor)
            
            original.updated_at = datetime.now()
            
            # Auditoría en Historia Clínica
            await ServicioBeneficiarios.registrar_auditoria(
                db, original.beneficiario_id, usuario_id, "MedicamentoBeneficiario", "Edición Histórica",
                original.id, "prescripcion", "Ver HistorialPrescripcion", "Nueva versión activa", motivo
            )

            await db.commit()
            return original

    @staticmethod
    async def asignar_alergia(beneficiario_id: int, alergia_id: int, datos: Dict[str, Any], usuario_id: int):
        async with AsyncSessionLocal() as db:
            asignacion = BeneficiarioAlergia(
                beneficiario_id=beneficiario_id,
                alergia_id=alergia_id,
                **datos
            )
            db.add(asignacion)
            
            await ServicioBeneficiarios.registrar_auditoria(
                db, beneficiario_id, usuario_id, "BeneficiarioAlergia", "Creación", 
                None, "alergia", None, f"ID Alergia: {alergia_id}"
            )
            await db.commit()
            return asignacion

    @staticmethod
    async def asignar_patologia(beneficiario_id: int, patologia_id: int, datos: Dict[str, Any], usuario_id: int):
        async with AsyncSessionLocal() as db:
            asignacion = BeneficiarioPatologia(
                beneficiario_id=beneficiario_id,
                patologia_id=patologia_id,
                **datos
            )
            db.add(asignacion)
            
            await ServicioBeneficiarios.registrar_auditoria(
                db, beneficiario_id, usuario_id, "BeneficiarioPatologia", "Creación", 
                None, "patologia", None, f"ID Patologia: {patologia_id}"
            )
            await db.commit()
            return asignacion

    @staticmethod
    async def editar_patologia(asignacion_id: int, nuevos_datos: Dict[str, Any], usuario_id: int, motivo: str):
        async with AsyncSessionLocal() as db:
            stmt = select(BeneficiarioPatologia).where(BeneficiarioPatologia.id == asignacion_id)
            result = await db.execute(stmt)
            original = result.scalar_one_or_none()
            
            if not original:
                raise ValidationError("Patología no encontrada")

            # Snapshot al historial
            historial = HistorialPatologia(
                beneficiario_patologia_id_original=original.id,
                beneficiario_id=original.beneficiario_id,
                patologia_id=original.patologia_id,
                nivel_dependencia=original.nivel_dependencia,
                genera_discapacidad=original.genera_discapacidad,
                notas=original.notas,
                motivo_cambio=motivo,
                modificado_por=usuario_id
            )
            db.add(historial)

            # Actualizar
            for campo, valor in nuevos_datos.items():
                setattr(original, campo, valor)
            
            original.updated_at = datetime.now()
            
            await ServicioBeneficiarios.registrar_auditoria(
                db, original.beneficiario_id, usuario_id, "BeneficiarioPatologia", "Edición Histórica",
                original.id, "patologia", "Ver HistorialPatologia", "Nueva versión", motivo
            )

            await db.commit()
            return original

    @staticmethod
    async def archivar_beneficiario(beneficiario_id: int, datos_egreso: Dict[str, Any], usuario_id: int):
        from app.models.beneficiarios import ExBeneficiarios
        import json
        
        async with AsyncSessionLocal() as db:
            # 1. Obtener beneficiario con relaciones
            stmt = select(Beneficiario).where(Beneficiario.id == beneficiario_id)
            result = await db.execute(stmt)
            b = result.scalar_one_or_none()
            
            if not b:
                raise ValidationError("Beneficiario no encontrado")

            # 2. Crear snapshot JSON (simplificado por ahora)
            snapshot = {
                "nombres": b.nombres,
                "apellidos": b.apellidos,
                "identificacion": b.identificacion,
                "fecha_nacimiento": str(b.fecha_nacimiento),
                "eps": b.eps,
                "tipo_sangre": b.tipo_sangre,
                "observaciones": b.observaciones
            }

            # 3. Crear registro ExBeneficiario
            ex = ExBeneficiarios(
                beneficiario_id_original=b.id,
                identificacion=b.identificacion,
                nombres=b.nombres,
                apellidos=b.apellidos,
                fecha_nacimiento=b.fecha_nacimiento,
                genero=b.genero,
                fecha_ingreso=b.fecha_ingreso,
                fecha_egreso=date.today(),
                motivo_egreso=datos_egreso.get("motivo_egreso", "Voluntario"),
                observaciones_egreso=datos_egreso.get("observaciones_egreso"),
                datos_completos_json=snapshot
            )
            db.add(ex)

            # 4. Auditoría clínica final
            await ServicioBeneficiarios.registrar_auditoria(
                db, b.id, usuario_id, "Beneficiario", "Egreso/Archivado", 
                b.id, "estado", "Activo", "Archivado", datos_egreso.get("motivo_egreso")
            )

            # 5. Eliminar (o marcar como inactivo) el registro original
            # Para este MVP, lo eliminaremos físicamente ya que tenemos la copia en ExBeneficiarios
            await db.delete(b)
            
            await db.commit()
            return ex
