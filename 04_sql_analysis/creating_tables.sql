CREATE DATABASE logistics_analytics;
USE logistics_analytics;


---------------------------------------------- CREATING LOGISTICS ANALYTICS TABLE -------------------------------------------------


CREATE TABLE freight_data (
    shipment_id INT PRIMARY KEY,
    shipment_date DATE,
    route VARCHAR(100),
    transport_mode VARCHAR(50),
    cargo_type VARCHAR(50),
    distance_km DECIMAL(10,2),
    weight_kg DECIMAL(12,2),
    demand_units INT,
    freight_cost DECIMAL(12,2),
    delivery_days DECIMAL(6,2),
    delivery_status VARCHAR(50),
    region VARCHAR(50)
);


---------------------------------------------- VERIFYING TABLE ------------------------------------------------------------

SHOW TABLE freight_data;
