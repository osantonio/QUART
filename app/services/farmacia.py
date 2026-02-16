from app.models.beneficiarios import Medicamento, CantidadMedicamento, Beneficiario
from app.config.database import AsyncSessionLocal
from app.utils.exceptions import ValidationError
from sqlmodel import select, func
from datetime import date, datetime
from typing import List, Dict, Any

class ServicioFarmacia:

    @staticmethod
    async def registrar_lote(datos: Dict[str, Any]) -> CantidadMedicamento:
        async with AsyncSessionLocal() as db:
            if not datos.get("medicamento_id") or not datos.get("cantidad_inicial"):
                raise ValidationError("Medicamento y cantidad inicial son obligatorios")
            
            # La cantidad disponible inicial es igual a la inicial
            datos["cantidad_disponible"] = datos["cantidad_inicial"]
            
            nuevo_lote = CantidadMedicamento(**datos)
            db.add(nuevo_lote)
            await db.commit()
            await db.refresh(nuevo_lote)
            return nuevo_lote

    @staticmethod
    async def obtener_resumen_inventario() -> List[Dict[str, Any]]:
        """Consolida el inventario agrupando por medicamento"""
        async with AsyncSessionLocal() as db:
            # Query para sumar cantidades por medicamento
            stmt = (
                select(
                    Medicamento.id,
                    Medicamento.nombre,
                    Medicamento.presentacion,
                    Medicamento.concentracion,
                    func.sum(CantidadMedicamento.cantidad_disponible).label("total_disponible"),
                    func.count(CantidadMedicamento.id).label("num_lotes")
                )
                .join(CantidadMedicamento)
                .group_by(Medicamento.id)
            )
            result = await db.execute(stmt)
            
            resumen = []
            for row in result:
                resumen.append({
                    "id": row.id,
                    "nombre": row.nombre,
                    "presentacion": row.presentacion,
                    "concentracion": row.concentracion,
                    "total_disponible": row.total_disponible,
                    "num_lotes": row.num_lotes
                })
            return resumen

    @staticmethod
    async def obtener_detalle_medicamento(medicamento_id: int) -> Dict[str, Any]:
        """Obtiene detalles de un medicamento y sus lotes, incluyendo asignaciones"""
        async with AsyncSessionLocal() as db:
            # Medicamento
            stmt_med = select(Medicamento).where(Medicamento.id == medicamento_id)
            res_med = await db.execute(stmt_med)
            medicamento = res_med.scalar_one_or_none()
            
            if not medicamento:
                raise ValidationError("Medicamento no encontrado")

            # Lotes (CantidadMedicamento) con Beneficiario si está asignado
            stmt_lotes = (
                select(CantidadMedicamento, Beneficiario.nombres, Beneficiario.apellidos)
                .outerjoin(Beneficiario, CantidadMedicamento.beneficiario_asignado_id == Beneficiario.id)
                .where(CantidadMedicamento.medicamento_id == medicamento_id)
                .order_by(CantidadMedicamento.fecha_vencimiento)
            )
            res_lotes = await db.execute(stmt_lotes)
            
            lotes = []
            for lote, b_nombres, b_apellidos in res_lotes:
                lote_dict = lote.model_dump()
                lote_dict["beneficiario_nombre"] = f"{b_nombres} {b_apellidos}" if b_nombres else "Stock General"
                lote_dict["esta_vencido"] = lote.fecha_vencimiento < date.today()
                lotes.append(lote_dict)

            return {
                "medicamento": medicamento.model_dump(),
                "lotes": lotes
            }

    @staticmethod
    async def descontar_stock(lote_id: int, cantidad: int):
        """Descuenta stock de un lote específico"""
        async with AsyncSessionLocal() as db:
            stmt = select(CantidadMedicamento).where(CantidadMedicamento.id == lote_id)
            result = await db.execute(stmt)
            lote = result.scalar_one_or_none()
            
            if not lote:
                raise ValidationError("Lote no encontrado")
            
            if lote.cantidad_disponible < cantidad:
                raise ValidationError(f"Stock insuficiente en el lote {lote.lote}. Disponible: {lote.cantidad_disponible}")
            
            lote.cantidad_disponible -= cantidad
            await db.commit()
            return lote
