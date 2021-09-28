author = "Sergio Esteban Tarrero"

from neo4j import GraphDatabase
from datetime import datetime
from datetime import timedelta


class Shipments(object):
    neo_connection = None

    def __init__(self, neo_driver):
        self.neo_connection = neo_driver.session()

    def shipping_manage(self, shipment_method, product, start_city, destination_city):
        # product pensabamos hacer algo con el pero al final no :D
        resp = self.neo_connection.run('MATCH (n:Ciudad) WHERE n.name="'+start_city+'" or n.name="'+destination_city+'" RETURN n')
        data = resp.data()
        l = len(data)
        if l != 2:
            print("CIUDAD DE DESTINO U ORIGEN NO VALIDA")
            return None
        if shipment_method == 1:
            datos = self.shipment_method_1(start_city, destination_city)
        elif shipment_method == 2:
            datos = self.shipment_method_2(start_city, destination_city)
        elif shipment_method == 3:
            datos = self.shipment_method_3(start_city, destination_city)
        else:
            print('Tipo de envio no valido')
            return None
        return datos

    def shipment_method_1(self, start_city, destination_city):
        actual_time = datetime.today()

        if actual_time.hour+1 >= 19:
            print('Se ha acabado el servicio de entrega por hoy, pruebe otro tipo de pedido')
            return None
        elif actual_time.hour < 8:
            max_time = datetime(actual_time.year, actual_time.month, actual_time.day, 19, 0, 0)
            starts_time = datetime(actual_time.year, actual_time.month, actual_time.day, 8, 0, 0)
            time_difference = max_time - starts_time - timedelta(hours=1)  # 1 h de empaquetado
        else:
            max_time = datetime(actual_time.year, actual_time.month, actual_time.day, 19, 0, 0)
            time_difference = max_time - actual_time - timedelta(hours=1)  # 1 h empaquetado

        minutes_difference = time_difference / timedelta(minutes=1)
        seconds_diff = minutes_difference * 60

        query = 'match (a:Ciudad{name : "'+start_city +'"}), (b:Ciudad{name :"'+destination_city+'"})' \
                ', ruta =  shortestPath((a)-[*]-(b))' \
                'using index a:Ciudad(name)' \
                ' using index b:Ciudad(name) with reduce(t=0, v in  relationships(ruta)  | t+v.tiempo) as tiempo, ' \
                'reduce(t=0, v in  relationships(ruta)  | t+v.precio) as precio, ' \
                '[rel in relationships(ruta) | rel.vehiculo] as vehiculo, ' \
                '[rel in relationships(ruta) | rel.tiempo] as tiempos_ciudad, ' \
                '[rel in nodes(ruta) | rel.name] as ciudades ' \
                'where tiempo < '+str(int(seconds_diff))+' ' \
                'return precio, ciudades, tiempo, vehiculo, tiempos_ciudad ' \
                'order by tiempo asc limit 1'
        result = self.neo_connection.run(query).data()
        if len(result) == 0:
            print("Lo sentimos es imposible que llegue hoy debido a la hora que es")
            return None

        datos = self.guardar_datos(result)

        return datos

    def shipment_method_2(self, start_city, destination_city):
        actual_time = datetime.today()
        next_day_time = actual_time + timedelta(days=1)
        next_day_time = datetime(next_day_time.year, next_day_time.month, next_day_time.day, 14, 0, 0)
        time_difference = next_day_time - actual_time - timedelta(hours=8) - timedelta(hours=1)
        # tiempo entre las 0 y 8h y el tiempo que tarda en empaquetarse 1 h
        minutes_difference = time_difference / timedelta(minutes=1)
        seconds_diff = minutes_difference * 60
        print("Obteniendo la ruta mas economica que cumpla las condiciones")
        query = 'match ruta = (a:Ciudad{name : "' + start_city + '"})-[*..3]-(b:Ciudad{name :"' + destination_city + '"})' \
                'using index a:Ciudad(name)' \
                ' using index b:Ciudad(name) ' \
                'with reduce(t=0, v in  relationships(ruta)  | t+v.tiempo) as tiempo, ' \
                'reduce(t=0, v in  relationships(ruta)  | t+v.precio) as precio, ' \
                '[rel in relationships(ruta) | rel.vehiculo] as vehiculo, ' \
                '[rel in relationships(ruta) | rel.tiempo] as tiempos_ciudad, ' \
                '[rel in nodes(ruta) | rel.name] as ciudades ' \
                'where tiempo < ' + str(int(seconds_diff)) + ' ' \
                'return precio, ciudades, tiempo, vehiculo, tiempos_ciudad ' \
                'order by precio asc limit 1'
        result = self.neo_connection.run(query).data()

        if len(result) == 0:
            print("El paquete tarda demasiado tiempo no se puede enviar")
            return None

        datos = self.guardar_datos(result)

        return datos

    def shipment_method_3(self, start_city, destination_city):

        query = 'match ruta = (a:Ciudad{name : "'+start_city+'"})-[*..3]-(b:Ciudad{name :"'+destination_city+'"})' \
                'using index a:Ciudad(name)' \
                ' using index b:Ciudad(name) with reduce(t=0, v in  relationships(ruta)  | t+v.tiempo) as tiempo, ' \
                'reduce(t=0, v in  relationships(ruta)  | t+v.precio) as precio, ' \
                '[rel in relationships(ruta) | rel.vehiculo] as vehiculo, ' \
                '[rel in relationships(ruta) | rel.tiempo] as tiempos_ciudad, ' \
                '[rel in nodes(ruta) | rel.name] as ciudades ' \
                'return precio, ciudades, tiempo, vehiculo, tiempos_ciudad ' \
                'order by precio asc limit 1'
        result = self.neo_connection.run(query).data()
        datos = self.guardar_datos(result)
        return datos

    def guardar_datos(self, result):
        datos = []
        vehiculo = ""
        paradas = ""
        tiempo_por_zona = ""
        precio_total = result[0]['precio']
        tiempo_total = result[0]['tiempo']
        for v in result[0]['vehiculo']:
            vehiculo += v + " "
        for t in result[0]['tiempos_ciudad']:
            tiempo_por_zona += str(t) + " "
        for c in result[0]['ciudades']:
            paradas += str(c) + " "
        paradas = paradas.rstrip()
        vehiculo = vehiculo.rstrip()
        tiempo_por_zona = tiempo_por_zona.rstrip()
        datos.append(paradas)
        datos.append(vehiculo)
        datos.append(tiempo_por_zona)
        datos.append(tiempo_total)
        datos.append(precio_total)
        print_info(datos, tiempo_total, precio_total)
        return datos


def print_info(datos, tiempo_total, precio_total):
    segundos = tiempo_total
    horas = int(segundos / 3600)
    segundos -= horas * 3600
    minutos = int(segundos / 60)
    segundos -= minutos * 60
    print(datos)
    for x in range(0, len(datos[0].split(" ")) - 1):
        print("El paquete va de " + datos[0].split(" ")[x] + " a " + datos[0].split(" ")[x + 1] + " en " +
              datos[1].split(" ")[x] + " y tarda " + str(int(datos[2].split(" ")[x]) / 60) + " minutos (aprox)")
    print("Tarda " + str(horas) + " horas, " + str(minutos) + " minutos, " + str(segundos) + " segundos")
    print("Coste total: " + str(precio_total) + "€")


class BDDD_Conection(object):
    neo_connection = None

    def __init__(self, neo_driver):
        self.neo_connection = neo_driver.session()

    def delete_database(self):
        self.neo_connection.run("MATCH (n) DETACH DELETE n")


class Package(object):
    neo_connection = None

    def __init__(self, neo_driver, datos):
        self.neo_connection = neo_driver.session()
        # datos.append(paradas)
        # datos.append(vehiculo)
        # datos.append(tiempo_por_zona)
        # datos.append(tiempo_total)
        # datos.append(precio_total)
        self.cities = datos[0].split(" ")
        self.vehicles = datos[1].split(" ")
        self.city_times = datos[2].split(" ")
        self.total_time = datos[3]
        self.total_cost = datos[4]
        self.package_name = datos[5]
        self.shipment_method = datos[6]

        self.rest_time = self.total_time

        self.create_package()

    def create_package(self):
        query = 'CREATE (p:Paquete {name:"' + self.package_name + '"}) WITH p as pack MATCH (a) WHERE a.name = "' + \
                self.cities[0] + '" CREATE (pack)-[r:Estaen{tiemporestante:' + str(self.total_time) + '}]->(a) RETURN r'
        print("package name " + self.package_name)
        print("ciudad origen " + self.cities[0])
        print("ciudad destino " + self.cities[-1])
        print("tiempo total " + str(self.total_time))
        print("tiempo a restas cuando avance " + self.city_times[0])
        print("len vehicles " + str(self.vehicles))
        print("len cities " + str(self.cities))
        print("len tiempos " + str(self.city_times))
        self.neo_connection.run(query)
        # exit()

        print('Se ha creado el paquete de tipo ' + str(self.shipment_method) + ': estamos en ' + self.cities[
            0] + ' por via ' + self.vehicles[0] + ' a ' + self.cities[1] + ' con destino final ' + self.cities[-1])

    def next_city(self):
        actual_city = self.actual_city()
        next_city = ''
        vehicle_index = 0
        if actual_city != self.cities[-1]:
            for i in range(0, len(self.cities)):
                if self.cities[i] == actual_city:
                    print(i)
                    next_city = self.cities[i + 1]
                    vehicle_index = i
        else:
            actual_city = None

        if actual_city is not None:
            print("--------------------------------------------------")
            print("|         actual city " + actual_city + "                |")
            print("|         next city " + next_city + "                |")
            print("|         next vehicle " + self.vehicles[vehicle_index] + "                |")
            print("|         time to arrive " + str(self.total_time) + "                |")
            print("--------------------------------------------------")
        # exit()
        if actual_city is None:
            print('El paquete ha llegado a su destino')
        elif next_city is self.cities[-1]:
            print('El paquete acaba de llegar a su destino: ' + next_city)
            query = 'MATCH (Paquete { name:"' + self.package_name + '" })-[r:Estaen]->(a) where a.name="' + self.cities[
                -2] + '" DELETE r'
            self.neo_connection.run(query)
            query = 'MATCH (p:Paquete { name:"' + self.package_name + '" }) DELETE p'
            self.neo_connection.run(query)
        else:
            query = 'MATCH (Paquete { name:"' + self.package_name + '" })-[r:Estaen]->(a) where a.name="' + actual_city + '" DELETE r'
            self.neo_connection.run(query)
            self.total_time = int(self.total_time) - int(self.city_times[vehicle_index])
            query = 'MERGE (p:Paquete {name:"' + self.package_name + '"}) WITH p as pack MATCH (a) WHERE a.name = "' + \
                    next_city + '" CREATE (pack)-[r:Estaen{tiemporestante:' + str(self.total_time) + '}]->(a) RETURN r'
            self.neo_connection.run(query)

    def actual_city(self):
        query = 'match (p:Paquete {name : "' + self.package_name + '"})-[]-(c) return c.name as name'
        message = self.neo_connection.run(query).data()
        # print(message)
        if message:
            ciudad_actual = message[0]['name']
        else:
            ciudad_actual = None
        return ciudad_actual

    def where_is_and_time_left(self):
        actual_city = self.actual_city()

        if actual_city is None:
            print('El paquete ha llegado a su destino')
            return

        query = 'MATCH (n:Paquete {name:"' + self.package_name + '"})-[r:Estaen]-(c) RETURN c.name as city_name, r.tiemporestante as tiempo_restante'
        message = self.neo_connection.run(query).data()
        ciudad_actual = message[0]['city_name']
        tiempo_restante = message[0]['tiempo_restante']
        self.calcular_tiempo_restante(tiempo_restante)

        shipment_day = dia_de_entrega(tiempo_restante)
        print('El paquete se encuentra en ' + ciudad_actual + ' y llegara a su destino el ' + shipment_day)

    def calcular_tiempo_restante(self, tiempo_restante):
        segundos = tiempo_restante
        horas = int(segundos / 3600)
        segundos -= horas * 3600
        minutos = int(segundos / 60)
        segundos -= minutos * 60
        print("Le queda al paquete " + str(horas) + " horas, " + str(minutos) + " minutos, " + str(
            segundos) + " segundos")


def dia_de_entrega(tiempo_restante):
    actual_time = datetime.today()
    # TODO: HORAS DE REPARTO 8 A 19 --> 11 HORAS, 13 HORAS SIN REPARTIR (SI NO SE REPARTE DESPUES DE LAS 19 HORAS MULTIPLICAR
    #  CADA DIA QUE TARDA POR 13 HORAS Y SUMARLO A LA HORA TOTAL DE ENVIO YA QUE SERIAN 13 QUE NO SE TRABAJA REPARTIENDO POR DIA)
    #  ACTUALMENTE LOS REPARTIDORES TRABAJAN 24H
    dias = 0
    segundos = tiempo_restante
    horas = int(segundos / 3600)
    while horas >= 24:
        dias += 1
        horas -= 24
    segundos -= horas * 3600
    minutos = int(segundos / 60)
    segundos -= minutos * 60
    fecha_llegada = actual_time + timedelta(days=dias,hours=horas,minutes=minutos,seconds=segundos)
    while fecha_llegada.hour < 8:
        fecha_llegada = fecha_llegada +timedelta(hours=1)
    # print(str(fecha_llegada).split(".")[0])
    return str(fecha_llegada).split(".")[0]


if __name__ == '__main__':
    neo_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))
    BBDD = BDDD_Conection(neo_driver)
    shipment = Shipments(neo_driver)
    # query_index = "CREATE INDEX ON:Ciudad(name)"
    # neo_driver.session().run(query_index)
    # query_index = "CREATE INDEX ON:Almacen(name)"
    # neo_driver.session().run(query_index)
    # exit()
    print("----------------------")

    package_list = shipment.shipping_manage(3, 'ISM', "Tenerife", "Barcelona")
    if package_list is not None:
        package_list.append("paquete1")
        package_list.append(3)
    print("----------------------")
    package_list2 = shipment.shipping_manage(1, 'ALIENFARE', "Madrid", "Valencia")
    if package_list2 is not None:
        package_list2.append("paquete2")
        package_list2.append(1)
    print("----------------------")

    package_list3 = shipment.shipping_manage(2, 'DEL', "Madrid", "Valladolid")
    if package_list3 is not None:
        package_list3.append("paquete3")
        package_list3.append(2)
    print("----------------------")

    print('\n')

    if package_list is not None:
        print("----------------------")
        paquete = Package(neo_driver, package_list)
        paquete.next_city()
        # exit()
        paquete.next_city()
        paquete.where_is_and_time_left()
        paquete.next_city()
        paquete.next_city()
        paquete.next_city()
        print("----------------------")
    if package_list2 is not None:
        print("----------------------")
        paquete2 = Package(neo_driver, package_list2)
        paquete2.next_city()
        # exit()
        paquete2.where_is_and_time_left()
        paquete2.next_city()
        paquete2.next_city()
        paquete2.next_city()
        paquete2.next_city()
        print("----------------------")
    if package_list3 is not None:
        print("----------------------")
        paquete3 = Package(neo_driver, package_list3)
        paquete3.next_city()
        # exit()
        paquete3.where_is_and_time_left()
        print("----------------------")
