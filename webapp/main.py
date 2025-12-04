from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from image_processor import ImageProcessor

app = FastAPI(title="Processamento de Imagens - Filtros Espaciais")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

processor = ImageProcessor()
sessions = {}

STUDENT_INFO = {
    "nome": "Ryan Oliveira",
    "curso": "Bacharelado em Ciência da Computação",
    "disciplina": "Processamento de Imagens",
    "turma": "CC8NA",
    "periodo": "2025.2",
    "professor": "Prof. Claudio Coutinho",
    "tema": "Aplicação de Filtros Espaciais para Redução de Ruído",
    "data_entrega": "2025-12-03"
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "student_info": STUDENT_INFO})

@app.get("/sobre", response_class=HTMLResponse)
async def sobre(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "student_info": STUDENT_INFO})

@app.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
    return templates.TemplateResponse("demo.html", {"request": request, "student_info": STUDENT_INFO})

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_path = UPLOAD_DIR / f"{session_id}_{file.filename}"
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        original = processor.load_image_from_bytes(content)
        original_b64 = processor.image_to_base64(original)

        sessions[session_id] = {
            "original": original,
            "filename": file.filename,
            "upload_time": datetime.now().isoformat(),
            "processed": False
        }

        return JSONResponse({
            "success": True,
            "session_id": session_id,
            "filename": file.filename,
            "image": original_b64,
            "shape": original.shape
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/process")
async def process_image(
    session_id: str = Form(...),
    noise_type: str = Form(...),
    salt_prob: float = Form(0.02),
    pepper_prob: float = Form(0.02),
    gaussian_sigma: float = Form(25.0)
):
    try:
        if session_id not in sessions:
            return JSONResponse({"success": False, "error": "Sessão não encontrada"}, status_code=404)

        original = sessions[session_id]["original"]

        if noise_type == "salt_pepper":
            noisy = processor.add_salt_pepper_noise(original, salt_prob=salt_prob, pepper_prob=pepper_prob)
        else:
            noisy = processor.add_gaussian_noise(original, sigma=gaussian_sigma)

        results = processor.process_image(original, noisy)
        stats = processor.get_summary_stats(results)

        response_data = {
            "success": True,
            "session_id": session_id,
            "noise_type": noise_type,
            "noisy_image": processor.image_to_base64(noisy),
            "stats": stats,
            "filters": {}
        }

        for filter_name, data in results.items():
            response_data["filters"][filter_name] = {
                "image": processor.image_to_base64(data['image']),
                "mse": round(data['mse'], 4),
                "psnr": round(data['psnr'], 4)
            }

        sessions[session_id]["results"] = results
        sessions[session_id]["noisy"] = noisy
        sessions[session_id]["noise_type"] = noise_type
        sessions[session_id]["stats"] = stats
        sessions[session_id]["processed"] = True

        return JSONResponse(response_data)

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/charts/{session_id}")
async def get_charts(session_id: str):
    try:
        if session_id not in sessions or not sessions[session_id].get("processed"):
            return JSONResponse({"success": False, "error": "Sessão não encontrada"}, status_code=404)

        results = sessions[session_id]["results"]
        filter_names = list(results.keys())
        mse_values = [results[f]['mse'] for f in filter_names]
        psnr_values = [results[f]['psnr'] for f in filter_names]

        fig_mse = go.Figure()
        fig_mse.add_trace(go.Bar(
            x=filter_names, y=mse_values, name='MSE',
            marker_color='rgb(55, 83, 109)',
            text=[f'{v:.2f}' for v in mse_values],
            textposition='auto',
        ))
        fig_mse.update_layout(title='MSE por Filtro', xaxis_title='Filtro', yaxis_title='MSE', height=400, template='plotly_white')

        fig_psnr = go.Figure()
        fig_psnr.add_trace(go.Bar(
            x=filter_names, y=psnr_values, name='PSNR',
            marker_color='rgb(26, 118, 255)',
            text=[f'{v:.2f}' for v in psnr_values],
            textposition='auto',
        ))
        fig_psnr.update_layout(title='PSNR por Filtro', xaxis_title='Filtro', yaxis_title='PSNR (dB)', height=400, template='plotly_white')

        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Scatter(
            x=mse_values, y=psnr_values, mode='markers+text',
            text=[f.replace(' ', '<br>') for f in filter_names],
            textposition='top center',
            marker=dict(size=12, color=psnr_values, colorscale='Viridis', showscale=True, colorbar=dict(title="PSNR (dB)")),
        ))
        fig_comparison.update_layout(title='MSE vs PSNR', xaxis_title='MSE', yaxis_title='PSNR (dB)', height=500, template='plotly_white')

        return JSONResponse({
            "success": True,
            "charts": {
                "mse": json.loads(fig_mse.to_json()),
                "psnr": json.loads(fig_psnr.to_json()),
                "comparison": json.loads(fig_comparison.to_json())
            }
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/export/{session_id}")
async def export_results(session_id: str):
    try:
        if session_id not in sessions or not sessions[session_id].get("processed"):
            return JSONResponse({"success": False, "error": "Sessão não encontrada"}, status_code=404)

        results = sessions[session_id]["results"]
        data = []
        for filter_name, metrics in results.items():
            data.append({
                'Filtro': filter_name,
                'MSE': f"{metrics['mse']:.4f}",
                'PSNR (dB)': f"{metrics['psnr']:.4f}"
            })

        df = pd.DataFrame(data)
        csv_path = RESULTS_DIR / f"resultados_{session_id}.csv"
        df.to_csv(csv_path, index=False)

        return FileResponse(csv_path, media_type='text/csv', filename=f"resultados_{sessions[session_id]['filename']}.csv")

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/info")
async def get_info():
    return JSONResponse({"success": True, "info": STUDENT_INFO})

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
