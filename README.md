Flujo de Trabajo
Estructura de Ramas:
Main: Versión final (producción)
Development: Integración inicial (base para módulos)
Testing: Entorno de pruebas unificado 
modulo1 a modulo12: Desarrollo por módulo

Cada módulo tendra su rama a base de Development
Aquí cada grupo subirá su código sobre su módulo
Luego de tener todo el código se subirá a Testing para probar el código
Si el código funciona perfectamente se subirá a Main para la entrega

Dejando así el flujo:
Development-(Modulo) --> Testing (General) --> Main (Versión final)

Notas:
1.No se tendra rama de Producción ya que esta será sustituida por la rama Main
Como no hace falta tener mas de una entrega en este proyecto Main cumplira la función de rama de entrega

2.No está permitido hacer Push o Merge directamente a Main, solo los administradores
(Modulo Integrador) harán esa función
