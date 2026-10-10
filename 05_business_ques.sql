                                           ==============   BUSINESS QUESTIONS   ===============



--Ques-1)Identify the top 5 routes with the highest total demand and number of shipments.
SELECT
    route,
    SUM(demand_units) AS total_demand,
    COUNT(shipment_id) AS total_shipments,
    ROUND(AVG(distance_km), 2) AS avg_distance
FROM freight_data
GROUP BY route
ORDER BY total_demand DESC
LIMIT 5;



--Ques-2)Find transport modes whose average freight cost is above the overall average freight cost.
SELECT
    transport_mode,
    ROUND(AVG(freight_cost), 2) AS avg_freight_cost,
    COUNT(*) AS total_shipments
FROM freight_data
GROUP BY transport_mode
HAVING AVG(freight_cost) > (
    SELECT AVG(freight_cost)
    FROM freight_data
)
ORDER BY avg_freight_cost DESC;



--Ques-3)Find regions where total demand exceeds 100,000 units and average delivery time is more than 3 days.
SELECT
    region,
    SUM(demand_units) AS total_demand,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days,
    COUNT(*) AS total_shipments
FROM freight_data
GROUP BY region
HAVING SUM(demand_units) > 100000
   AND AVG(delivery_days) > 3
ORDER BY total_demand DESC;



--Ques-4)Calculate monthly demand, monthly freight expenditure, and average delivery time.
SELECT
    YEAR(shipment_date) AS shipment_year,
    MONTH(shipment_date) AS shipment_month,
    SUM(demand_units) AS total_demand,
    ROUND(SUM(freight_cost), 2) AS total_freight_cost,
    ROUND(AVG(delivery_days), 2) AS avg_delivery_days
FROM freight_data
GROUP BY
    YEAR(shipment_date),
    MONTH(shipment_date)
ORDER BY
    shipment_year,
    shipment_month;



--Ques-5)Which routes have the highest demand, along with their transport modes.
SELECT
    f.route,
    f.transport_mode,
    r.total_demand
FROM freight_data AS f
JOIN route_summary AS r
    ON f.route = r.route
GROUP BY
    f.route,
    f.transport_mode,
    r.total_demand
ORDER BY r.total_demand DESC;



--Ques-6)Find total demand and shipment count for each route, including its origin and destination.
SELECT
    r.route,
    r.origin_city,
    r.destination_city,
    COUNT(f.shipment_id) AS total_shipments,
    SUM(f.demand_units) AS total_demand
FROM route_master AS r
INNER JOIN freight_data AS f
    ON r.route = f.route
GROUP BY
    r.route,
    r.origin_city,
    r.destination_city
ORDER BY total_demand DESC;



--Ques-7)Find transport modes whose actual average freight cost is higher than the estimated cost based on distance.
SELECT
    f.transport_mode,
    COUNT(*) AS total_shipments,
    ROUND(AVG(f.freight_cost), 2) AS actual_avg_cost,
    ROUND(AVG(f.distance_km * t.cost_per_km), 2)
        AS estimated_avg_cost
FROM freight_data AS f
INNER JOIN transport_rates AS t
    ON f.transport_mode = t.transport_mode
GROUP BY f.transport_mode
HAVING AVG(f.freight_cost) >
       AVG(f.distance_km * t.cost_per_km)
ORDER BY actual_avg_cost DESC;



--Ques-8)Find regions where total demand is greater than the average regional demand.
SELECT
    f.region,
    SUM(f.demand_units) AS total_demand,
    COUNT(f.shipment_id) AS total_shipments
FROM freight_data AS f
INNER JOIN (
    SELECT
        region,
        SUM(demand_units) AS regional_demand
    FROM freight_data
    GROUP BY region
) AS r
    ON f.region = r.region
GROUP BY f.region
HAVING SUM(f.demand_units) > (
    SELECT AVG(regional_total)
    FROM (
        SELECT SUM(demand_units) AS regional_total
        FROM freight_data
        GROUP BY region
    ) AS regional_summary
)
ORDER BY total_demand DESC;



--Ques-9)Find transport modes with above-average shipment volume and show their total demand and freight cost.
SELECT
    t.transport_mode,
    COUNT(f.shipment_id) AS total_shipments,
    SUM(f.demand_units) AS total_demand,
    ROUND(SUM(f.freight_cost), 2) AS total_freight_cost
FROM transport_rates AS t
INNER JOIN freight_data AS f
    ON t.transport_mode = f.transport_mode
GROUP BY t.transport_mode
HAVING COUNT(f.shipment_id) > (
    SELECT AVG(shipment_count)
    FROM (
        SELECT COUNT(*) AS shipment_count
        FROM freight_data
        GROUP BY transport_mode
    ) AS mode_summary
)
ORDER BY total_demand DESC;



--Ques-10)Find routes whose total demand is greater than the average route demand.
WITH route_demand AS (
    SELECT
        route,
        SUM(demand_units) AS total_demand
    FROM freight_data
    GROUP BY route
),
avg_route_demand AS (
    SELECT AVG(total_demand) AS avg_demand
    FROM route_demand
)
SELECT
    rd.route,
    rd.total_demand
FROM route_demand AS rd
CROSS JOIN avg_route_demand AS a
WHERE rd.total_demand > a.avg_demand
ORDER BY rd.total_demand DESC;



--Ques-11)Find the top 3 routes by total demand.
WITH route_demand AS (
    SELECT
        route,
        SUM(demand_units) AS total_demand
    FROM freight_data
    GROUP BY route
)
SELECT
    route,
    total_demand
FROM route_demand
ORDER BY total_demand DESC
LIMIT 3;



--Ques-12)Rank transport modes by total demand.
WITH mode_demand AS (
    SELECT
        transport_mode,
        SUM(demand_units) AS total_demand
    FROM freight_data
    GROUP BY transport_mode
)
SELECT
    transport_mode,
    total_demand,
    RANK() OVER (
        ORDER BY total_demand DESC
    ) AS demand_rank
FROM mode_demand;



--Ques-13)Find each route's most recent shipment.
WITH ranked_shipments AS (
    SELECT
        shipment_id,
        route,
        shipment_date,
        demand_units,
        ROW_NUMBER() OVER (
            PARTITION BY route
            ORDER BY shipment_date DESC, shipment_id DESC
        ) AS rn
    FROM freight_data
)
SELECT
    shipment_id,
    route,
    shipment_date,
    demand_units
FROM ranked_shipments
WHERE rn = 1;



--Ques-14)Compare each month's demand with the previous month.
WITH monthly_demand AS (
    SELECT
        DATE_FORMAT(shipment_date, '%Y-%m') AS month,
        SUM(demand_units) AS total_demand
    FROM freight_data
    GROUP BY DATE_FORMAT(shipment_date, '%Y-%m')
),
demand_comparison AS (
    SELECT
        month,
        total_demand,
        LAG(total_demand) OVER (
            ORDER BY month
        ) AS previous_month_demand
    FROM monthly_demand
)
SELECT
    month,
    total_demand,
    previous_month_demand,
    total_demand - previous_month_demand AS demand_change
FROM demand_comparison
ORDER BY month;



--Ques-15)Calculate cumulative demand over time.
WITH monthly_demand AS (
    SELECT
        DATE_FORMAT(shipment_date, '%Y-%m') AS month,
        SUM(demand_units) AS total_demand
    FROM freight_data
    GROUP BY DATE_FORMAT(shipment_date, '%Y-%m')
)
SELECT
    month,
    total_demand,
    SUM(total_demand) OVER (
        ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_demand
FROM monthly_demand
ORDER BY month;



----------------------------------------------------------------- END ---------------------------------------------------------------------------------------------
