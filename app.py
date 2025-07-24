from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def cuestionario():
    if request.method == 'POST':
        respuestas = request.form.to_dict()
        puntos_riesgo = 0

        if respuestas.get("p1_hipertension") == 's': puntos_riesgo += 1
        if respuestas.get("p2_diabetes") == 's': puntos_riesgo += 1

        peso = float(respuestas.get("p3_peso", 0))
        estatura = float(respuestas.get("p4_estatura", 1))
        imc = peso / (estatura ** 2)
        if imc >= 30: puntos_riesgo += 1

        if respuestas.get("p5_ejercicio") == 'n': puntos_riesgo += 1
        if int(respuestas.get("p9_frecuencia", 0)) < 2: puntos_riesgo += 1

        for clave in [
            "p13_fuma", "p15_sustancias", "p16_alcohol", "p18_cardio",
            "p19_conciencia", "p20_convulsiones", "p21_neuro", "p22_cabeza",
            "p23_luz", "p24_desorientado", "p25_mov_invol",
            "p26_medic_infancia", "p27_medic_1216"
        ]:
            if respuestas.get(clave) == 's':
                puntos_riesgo += 1
            
        if respuestas.get("p13_fuma") == 's' and int(respuestas.get("p14_cigarrillos", 0)) >= 5:
            puntos_riesgo += 1

        puntos_totales = 20
        porcentaje_riesgo = (puntos_riesgo / puntos_totales) * 100
        resultado = "Bajo Riesgo"
        if porcentaje_riesgo >= 70:
            resultado = "Alto Riesgo"
        elif porcentaje_riesgo >= 40:
            resultado = "Riesgo Moderado"

        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="si_no_apto"
            )
            cursor = conexion.cursor()
            consulta = '''INSERT INTO evaluaciones (
                peso, estatura, imc, puntos_riesgo, porcentaje_riesgo, resultado,
                p1_hipertension, p2_diabetes, p3_peso, p4_estatura, p5_ejercicio,
                p6_bajo_impacto, p7_medio_impacto, p8_alto_impacto, p9_frecuencia,
                p10_carbohidratos, p11_proteinas, p12_grasas, p13_fuma, p14_cigarrillos,
                p15_sustancias, p16_alcohol, p17_frec_alcohol, p18_cardio, p19_conciencia,
                p20_convulsiones, p21_neuro, p22_cabeza, p23_luz, p24_desorientado,
                p25_mov_invol, p26_medic_infancia, p27_medic_1216
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            datos = (
                peso, estatura, imc, puntos_riesgo, porcentaje_riesgo, resultado,
                respuestas.get("p1_hipertension"), respuestas.get("p2_diabetes"), peso,
                estatura, respuestas.get("p5_ejercicio"), respuestas.get("p6_bajo_impacto"),
                respuestas.get("p7_medio_impacto"), respuestas.get("p8_alto_impacto"),
                int(respuestas.get("p9_frecuencia", 0)), respuestas.get("p10_carbohidratos"),
                respuestas.get("p11_proteinas"), respuestas.get("p12_grasas"),
                respuestas.get("p13_fuma"), int(respuestas.get("p14_cigarrillos", 0)),
                respuestas.get("p15_sustancias"), respuestas.get("p16_alcohol"),
                respuestas.get("p17_frec_alcohol"), respuestas.get("p18_cardio"),
                respuestas.get("p19_conciencia"), respuestas.get("p20_convulsiones"),
                respuestas.get("p21_neuro"), respuestas.get("p22_cabeza"),
                respuestas.get("p23_luz"), respuestas.get("p24_desorientado"),
                respuestas.get("p25_mov_invol"), respuestas.get("p26_medic_infancia"),
                respuestas.get("p27_medic_1216")
            )
            cursor.execute(consulta, datos)
            conexion.commit()
            cursor.close()
            conexion.close()
        except Exception as e:
            return f" Error al guardar en la base de datos: {e}"

        return render_template("resultado.html", resultado=resultado, porcentaje=porcentaje_riesgo)

    return render_template("formulario.html")

if __name__ == '__main__':
    app.run(debug=True)
