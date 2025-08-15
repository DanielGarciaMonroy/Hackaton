from fastmcp import FastMCP
import subprocess
import uuid
from typing import Dict, Any
import os

import requests

mcp = FastMCP("Demo 🚀")
 
# Almacén simple de trabajos
JOBS: Dict[str, Dict[str, Any]] = {}

def _actualizar_estado_job(job_id: str) -> None:
    """Refresca el estado del job si terminó (uso interno)."""
    job = JOBS.get(job_id)
    if not job or job["status"] != "running":
        return
    proc: subprocess.Popen = job["process"]
    rc = proc.poll()
    if rc is None:
        return
    stdout, stderr = proc.communicate()
    job["stdout"] = stdout
    job["stderr"] = stderr
    job["returncode"] = rc
    job["status"] = "ok" if rc == 0 else "error"
def send_post_request(name:str) -> None:
    """Envía una solicitud POST a la URL especificada al finalizar el trabajo."""
    url = "https://friendly-train-67wx9qx6r5fw4j-8000.app.github.dev/calls"
    
    payload = {
        "caller": "Soporte",
        "clientName": "Daniel García Monroy",
        "service": name,
        "severity": "Alta",
        "sentiment": "Positivo",
        "duration": 120,
        "status": "Completada"
    }
    

    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        print(f"POST request sent successfully for job_id={"1"}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send POST request for job_id={"1"}: {e}")


@mcp.tool()

def azure_cli(command: str) -> str:
    
    """Ejecuta un comando en la CLI y retorna su salida estándar o error."""
    print("Ejecutando comando en Azure CLI:", command)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        send_post_request("Resource Group")
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"
 
@mcp.tool()
def crear_vm(name) -> dict:
    """
    Lanza la creación de una VM en segundo plano y retorna inmediatamente.
    Usa 'job_status' para consultar el resultado.
    """
    
    comando = [
        "az", "vm", "create",
        "--resource-group", "prueba",
        "--name", name,
        "--image", "Ubuntu2204",
        "--admin-username", "azureuser",
        "--generate-ssh-keys"
    ]
    print(comando)
    job_id = str(uuid.uuid4())
    print(f"Lanzando creación de VM (job_id={job_id}) ...")
    # Ejecutar en background
    proc = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    JOBS[job_id] = {
        "type": "crear_vm",
        "command": comando,
        "process": proc,
        "status": "running",
        "stdout": None,
        "stderr": None,
        "returncode": None
    }
    send_post_request("Virtual Machines")
    return {"job_id": job_id, "status": "running"}
 
@mcp.tool()
def job_status(job_id: str) -> dict:
    """
    Devuelve el estado de un job. Si terminó, incluye salida.
    """
    job = JOBS.get(job_id)
    if not job:
        return {"error": "Job no encontrado"}
    _actualizar_estado_job(job_id)
    return {
        "job_id": job_id,
        "status": job["status"],
        "returncode": job["returncode"],
        "stdout": job["stdout"],
        "stderr": job["stderr"]
    }
 
@mcp.tool()
def listar_jobs() -> dict:
    """
    Lista los jobs y su estado (sin forzar lectura si siguen corriendo).
    """
    resumen = {}
    for jid, data in JOBS.items():
        _actualizar_estado_job(jid)
        resumen[jid] = {
            "type": data["type"],
            "status": data["status"],
            "returncode": data["returncode"]
        }
    return resumen
 
if __name__ == "__main__":
    
    mcp.run(transport="http")