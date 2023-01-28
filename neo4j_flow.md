## Crear nodos principales:
```python
CREATE (bar:Ciudad {name:'Barcelona'}), 
       (cad:Ciudad {name:'Cadiz'}), 
       (form:Ciudad {name:'Formentera'}), 
       (lug:Ciudad {name:'Lugo'}), 
       (mad:Ciudad {name:'Madrid'}), 
       (ten:Ciudad {name:'Tenerife'}), 
       (val:Ciudad {name:'Valencia'}), 
       (vall:Ciudad {name:'Valladolid'})
RETURN bar, cad, form, lug, mad, ten, val, vall
```

## Crear nodos intermedios:
```python
CREATE (a:Almacen {name:'Amazon-Cuenca'}),
       (b:Almacen {name:'Correos-Zaragoza'}), 
       (c:Almacen {name:'MRW-Segovia'}),
       (d:Almacen {name:'Nacex-Zamora'}),
       (e:Almacen {name:'Seur-Cordoba'})
RETURN a,b,c,d,e
```

## Ver todos los nodos
```python
MATCH (n) 
RETURN n
```

## Creación de las relaciones
```python
# Relacion Amazon-Cuenca-Valencia
MATCH (a:Ciudad {name: "Valencia"}), (b:Almacen {name: "Amazon-Cuenca"})
CREATE (a)-[r1:Coche {tiempo:7800, precio:2,vehiculo:"Coche" }]->(b),
(a)-[r2:Ferrocarril {tiempo:7200, precio:(1.6),vehiculo:"Ferrocarril" }]->(b),
(a)-[r3:Avion {tiempo:6000, precio:7,vehiculo:"Avion" }]->(b)

# Relacion Barcelona-Madrid 
MATCH (a:Ciudad {name: "Barcelona"}), (b:Ciudad {name: "Madrid"})
CREATE (a)-[r1:Avion {tiempo: 18900, precio: 22.05, vehiculo: "Avion"}]->(b),
(a)-[r2:Coche {tiempo: 24570, precio: 6.3, vehiculo: "Coche"}]->(b)

# Relacion Cadiz-Amazon-Cuenca
MATCH (a:Ciudad {name: "Cadiz"}), (b:Almacen {name: "Amazon-Cuenca"})
MERGE (a)-[r1:Ferrocarril {tiempo:25200, precio:(5.6),vehiculo:"Ferrocarril" }]->(b)
MERGE (a)-[r2:Coche {tiempo:27300, precio:7,vehiculo:"Coche" }]->(b)

# Relacion Cadiz-Tenerife
MATCH (a:Ciudad {name:"Cadiz"}), (b:Ciudad {name:"Tenerife"})
CREATE (a)-[r1:Avion {tiempo:12000, precio:56, vehiculo:"Avion"}]->(b)
CREATE (a)-[r2:Ferrocarril {tiempo:57600, precio:16, vehiculo:"Ferrocarril"}]->(b)
CREATE (a)-[r3:Barco {tiempo:116400, precio:(4.8), vehiculo:"Barco"}]->(b)

# Relacion Correos-Zaragoza-Barcelona
MATCH (a:Ciudad), (b:Almacen)
WHERE a.name = "Barcelona" AND b.name = "Correos-Zaragoza"
CREATE (a)-[r1:Ferrocarril {tiempo:9600, precio:(2.4),vehiculo:"Ferrocarril" }]->(b),
(a)-[r2:Coche {tiempo:11000, precio:3,vehiculo:"Coche" }]->(b),
(a)-[r3:Avion {tiempo:4200, precio:(10.5),vehiculo:"Avion" }]->(b)

# Relacion Formentera-Barcelona
MATCH (a:Ciudad {name: "Barcelona"}), (b:Ciudad {name: "Formentera"})
MERGE (a)-[r:Avion {tiempo:5940, precio:(20.65),vehiculo:"Avion" }]->(b)
MERGE (a)-[r:Barco {tiempo:43680, precio:(1.77),vehiculo:"Barco" }]->(b)

# //Relacion Madrid-Amazon-Cuenca
MATCH (a:Ciudad {name: "Madrid"}), (b:Almacen {name: "Amazon-Cuenca"})
MERGE (a)-[r:Envio]->(b)
ON CREATE SET r.tiempoCoche = 6630, r.precioCoche = 1.7, r.tiempoFerrocarril = 6120, r.precioFerrocarril = 1.36, r.tiempoAvion = 5100, r.precioAvion = 5.95

# Relacion Madrid-Correos-Zaragoza
MATCH (a:Ciudad {name: "Madrid"}), (b:Almacen {name: "Correos-Zaragoza"})
CREATE (a)-[:Avion {tiempo:4200, precio:(10.5),vehiculo:"Avion" }]->(b),
       (a)-[:Coche {tiempo:11000, precio:3,vehiculo:"Coche" }]->(b),
       (a)-[:Ferrocarril {tiempo:9600, precio:(2.4),vehiculo:"Ferrocarril" }]->(b)

# Relacion Madrid-MRW-Segovia

```
