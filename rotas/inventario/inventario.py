import json
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import asyncpg
from database.conn import get_db

router = APIRouter(
    prefix="/api/v1/inventario",
    tags=["Inventário de Máquinas"]
)

class CpuSchema(BaseModel):
    nome: Optional[str]
    fabricante: Optional[str]
    nucleos: Optional[int]
    processadores_logicos: Optional[int]
    clock_max_ghz: Optional[float]
    id_processador: Optional[str]
    soquete: Optional[str]

class RamSchema(BaseModel):
    slot: Optional[str]
    capacidade_gb: Optional[float]
    velocidade: Optional[int]
    velocidade_configurada: Optional[int]
    tipo: Optional[str]

class DiscoSchema(BaseModel):
    modelo: Optional[str]
    serial: Optional[str]
    tipo: Optional[Any]
    tipoBus: Optional[Any]
    status: Optional[str]
    total: Optional[float]
    livre: Optional[float]
    usado: Optional[float]
    pUsado: Optional[float]

class GpuSchema(BaseModel):
    nome: Optional[str]
    processador_video: Optional[str]
    vram_gb: Optional[float]
    versao_driver: Optional[str]
    data_driver: Optional[str]
    resolucao: Optional[str]
    taxa_atualizacao: Optional[int]
    status: Optional[str]

class MonitorSchema(BaseModel):
    fabricante: Optional[str]
    modelo: Optional[str]
    numero_serie: Optional[str]
    ativo: Optional[bool]

class ProgramaSchema(BaseModel):
    nome_exibicao: Optional[str]
    versao: Optional[str]
    publicador: Optional[str]

class ConexaoSchema(BaseModel):
    nome: Optional[str]
    fabricante: Optional[str]
    class_guid: Optional[str]
    pnp_class: Optional[str]
    device_id: Optional[str]
    pnp_device_id: Optional[str]
    status: Optional[str]

class UsuarioLocalSchema(BaseModel):
    nome: Optional[str]
    nome_completo: Optional[str]
    desabilitado: Optional[bool]
    descricao: Optional[str]

class PayloadSchema(BaseModel):
    nome_computador: str
    dominio: Optional[str]
    usuario_atual: Optional[str]
    fabricante: Optional[str]
    modelo: Optional[str]
    familia_sistema: Optional[str]
    placa_mae_fabricante: Optional[str]
    placa_mae_produto: Optional[str]
    placa_mae_serial: Optional[str]
    sistema_operacional: Optional[str]
    versao_so: Optional[str]
    arquitetura: Optional[str]
    ips_internos: Optional[str]
    ip_publico: Optional[str]
    
    cpu: Optional[CpuSchema]
    ram: Optional[List[RamSchema]] = []
    memoria: Optional[List[DiscoSchema]] = []
    gpus: Optional[List[GpuSchema]] = []
    monitores: Optional[List[MonitorSchema]] = []
    programas: Optional[List[ProgramaSchema]] = []
    conexoes: Optional[List[ConexaoSchema]] = []
    usuarios_locais: Optional[List[UsuarioLocalSchema]] = []

class InventarioRequest(BaseModel):
    payload: PayloadSchema

@router.post("/")
async def receber_inventario(request: InventarioRequest, db: asyncpg.Connection = Depends(get_db)):
    p = request.payload

    query = """
        INSERT INTO maquinas_inventario (
            nome_computador, dominio, usuario_atual, fabricante, modelo, familia_sistema,
            placa_mae_fabricante, placa_mae_produto, placa_mae_serial, sistema_operacional,
            versao_so, arquitetura, ips_internos, ip_publico, cpu, ram, memoria_discos,
            gpus, monitores, programas, conexoes, usuarios_locais, atualizado_em
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, 
            $18, $19, $20, $21, $22, NOW()
        ) 
        ON CONFLICT (nome_computador) DO UPDATE SET
            dominio = EXCLUDED.dominio,
            usuario_atual = EXCLUDED.usuario_atual,
            fabricante = EXCLUDED.fabricante,
            modelo = EXCLUDED.modelo,
            familia_sistema = EXCLUDED.familia_sistema,
            placa_mae_fabricante = EXCLUDED.placa_mae_fabricante,
            placa_mae_produto = EXCLUDED.placa_mae_produto,
            placa_mae_serial = EXCLUDED.placa_mae_serial,
            sistema_operacional = EXCLUDED.sistema_operacional,
            versao_so = EXCLUDED.versao_so,
            arquitetura = EXCLUDED.arquitetura,
            ips_internos = EXCLUDED.ips_internos,
            ip_publico = EXCLUDED.ip_publico,
            cpu = EXCLUDED.cpu,
            ram = EXCLUDED.ram,
            memoria_discos = EXCLUDED.memoria_discos,
            gpus = EXCLUDED.gpus,
            monitores = EXCLUDED.monitores,
            programas = EXCLUDED.programas,
            conexoes = EXCLUDED.conexoes,
            usuarios_locais = EXCLUDED.usuarios_locais,
            atualizado_em = NOW();
    """

    try:
        await db.execute(
            query,
            p.nome_computador, p.dominio, p.usuario_atual, p.fabricante, p.modelo, p.familia_sistema,
            p.placa_mae_fabricante, p.placa_mae_produto, p.placa_mae_serial, p.sistema_operacional,
            p.versao_so, p.arquitetura, p.ips_internos, p.ip_publico,
            json.dumps(p.cpu.model_dump()) if p.cpu else None,
            json.dumps([r.model_dump() for r in p.ram]),
            json.dumps([m.model_dump() for m in p.memoria]),
            json.dumps([g.model_dump() for g in p.gpus]),
            json.dumps([m.model_dump() for m in p.monitores]),
            json.dumps([pr.model_dump() for pr in p.programas]),
            json.dumps([c.model_dump() for c in p.conexoes]),
            json.dumps([u.model_dump() for u in p.usuarios_locais])
        )
        return {"status": "sucesso", "mensagem": f"Inventário de {p.nome_computador} atualizado com sucesso."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {str(e)}")