# sheinpulse-mlops
**End-to-End MLOps Pipeline for Shein Product Analytics (Scraping → ML → API → Dashboard → Docker)**

## Overview
**SheinPulse** is an end-to-end machine learning project that collects product data from **Shein** via web scraping, cleans and engineers features, trains ML models with experiment tracking using **MLflow**, serves predictions through a **FastAPI** backend, and visualizes insights in a **React** dashboard — all deployed using **Docker**.

---

## Project Goal
Build a system that can:
1. **Scrape Shein product data** (name, price, discount, rating, reviews, category, images, etc.)
2. **Clean + prepare** the dataset for ML
3. **Train models** to predict a target such as:
   - **Popularity score** (e.g., based on reviews/ratings)
   - **Demand proxy** (estimated sales likelihood)
   - **Discount impact** (how discount correlates with popularity)
4. Track experiments using **MLflow**
5. Expose predictions via **FastAPI**
6. Display analytics and predictions in **React**
7. Deploy everything with **Docker Compose**

---

## Key Features
- Web scraping pipeline for Shein products  
- Data cleaning + feature engineering  
- ML training with evaluation metrics  
- MLflow experiment tracking + model registry  
- FastAPI prediction endpoint  
- React dashboard (charts + product explorer)  
- Dockerized services for easy deployment  
