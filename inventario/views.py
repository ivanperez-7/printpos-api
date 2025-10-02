from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view()
@permission_classes([IsAuthenticated])
def get_tabla_precios_simples(request):
    with connection.cursor() as cursor:
        cursor.execute("""
        WITH costo_produccion AS (
            SELECT  P.id producto_id,
                    COALESCE(SUM(PUI.utiliza_inventario * I.precio_lote / I.tamano_lote), 0.0) AS costo
            FROM    inventario_producto AS P
                    LEFT JOIN inventario_productoutilizainventario AS PUI
                        ON P.id = PUI.producto_id
                    LEFT JOIN inventario_inventario AS I
                        ON PUI.inventario_id = I.id
            GROUP   BY 1
            ORDER   BY 1 ASC
        )
        SELECT  P.id,
                P.codigo,
                CASE
                    WHEN P_Inv.producto_id IS NOT NULL THEN
                        P.descripcion
                        || CASE 
                            WHEN desde > 1 
                                THEN ', desde ' || ROUND(desde::numeric, 0)::text || ' unidades ' 
                            ELSE '' 
                        END
                        || CASE 
                            WHEN P_Inv.duplex 
                                THEN '[PRECIO DUPLEX]' 
                            ELSE '' 
                        END
                    ELSE 
                        P.descripcion
                END                                                             AS descripcion,
                P.abreviado,
                COALESCE(P_Inv.precio_con_iva, P_gran.precio_m2)                AS precio_con_iva,
                COALESCE(P_Inv.precio_con_iva, P_gran.precio_m2) / 1.16         AS precio_sin_iva,
                C_Prod.costo                                                    AS costo_prod,
                COALESCE(P_Inv.precio_con_iva, P_gran.precio_m2) - C_Prod.costo AS utilidad
        FROM    inventario_producto AS P
                LEFT JOIN inventario_productointervalo AS P_Inv
                    ON P.id = P_Inv.producto_id
                LEFT JOIN inventario_productogranformato AS P_gran
                    ON P.id = P_gran.producto_id
                JOIN costo_produccion AS C_Prod
                    ON P.id = C_Prod.producto_id
        WHERE   P.is_active = 'true'
        ORDER   BY 1 ASC;
        """)
        cols = ['id', 'codigo', 'descripcion', 'precio_con_iva', 'precio_sin_iva', 'costo_prod', 'utilidad']
        return Response(data=[dict(zip(cols, row)) for row in cursor.fetchall()], status=200)
