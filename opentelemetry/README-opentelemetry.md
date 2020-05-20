[HOME](../README.md)
# Opentelemetry examples
Примеры использования и установки Opentelemetry.


Opentelemetry может использоваться для трассировки, получения метрик и журналирования (логирования).


OpenTracing - это API, с которым ваш код будет взаимодействовать напрямую.

"По сути, ваше приложение будет «инструментировано» с использованием OpenTracing API, а конкретный трассировщик (например, Jaeger или Brave / Zipkin) будет собирать данные и отправлять их куда-нибудь. Это позволяет вашему приложению использовать нейтральный API во всем коде, чтобы вы могли переходить от одного провайдера к другому без необходимости изменения всей базы кода."

## Полезные ресурсы

 [Opentelemetry project](https://opentelemetry.io/)  
 [Слияние OpenTracing и OpenCensus: путь к конвергенции](https://habr.com/ru/company/southbridge/blog/464001/)  
 [Opentelemetry registry](https://opentelemetry.io/registry/)  
 [community](https://github.com/open-telemetry/community)  
 [OpenTelemetry — Voronezh Toptal Meetup (обзорное видео на русском про OpenTelemetry)](https://www.youtube.com/watch?v=Tf0uMwTrEd8)  
 [https://medium.com/opentelemetry](https://medium.com/opentelemetry)
 
 
 [Open tracing](https://opentracing.io/docs/overview/)  
 [OpenTracing Tutorial - Python](https://github.com/yurishkuro/opentracing-tutorial/tree/master/python)  
 https://opentelemetry-python.readthedocs.io/en/latest/  
 https://opentelemetry-python.readthedocs.io/en/latest/getting-started.html
 

 [Тушим пожар. Трассировка с OpenTracing и Jaeger.](https://medium.com/@aablinov/%D1%82%D1%83%D1%88%D0%B8%D0%BC-%D0%BF%D0%BE%D0%B6%D0%B0%D1%80-%D1%82%D1%80%D0%B0%D1%81%D1%81%D0%B8%D1%80%D0%BE%D0%B2%D0%BA%D0%B0-%D1%81-opentracing-%D0%B8-jaeger-69f0ae553b86)  
 [Конспект "Трейсинг распределенных систем. Егор Мыскин"](https://aladmit.com/summary/2019/02/01/summary-tracing.html)  
 [Opentelemetry Jaeger Exporter](https://opentelemetry-python.readthedocs.io/en/stable/ext/jaeger/jaeger.html#api)  
 [Системы распределенной трассировки - лучшие программные решения](https://overcoder.net/manuals/sistemy-raspredelennoj-trassirovki-luchshie-resheniya)
    
 [Jaeger](https://www.jaegertracing.io/)  
 [Jaeger getting started](https://www.jaegertracing.io/docs/1.18/getting-started/)  
 [Jaeger docker images](https://www.jaegertracing.io/download/#docker-images)  
 

## Install opentelemetry

> pip install opentelemetry-api  
> pip install opentelemetry-sdk


Для поддержки Jaeger следует установить:

> pip install opentelemetry-ext-jaeger

 Для поддержки Flask следует установить:
> pip install opentelemetry-ext-flask  
> pip install opentelemetry-ext-requests


## Запуск Jaeger в docker
Получить контейнер с Jaeger-ом:  
> docker pull jaegertracing/all-in-one:1.18  

Запустить контейнер:  
>docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 9411:9411 \
  jaegertracing/all-in-one:1.18

Ui Jaeger-а можно посмотреть по адрtсу http://localhost:16686

## Примеры

Для  запуска примеров следует установить пакеты opentelemetry.

Исходники примеров можно взять [здесь](https://github.com/open-telemetry/opentelemetry-python/tree/master/docs/examples).

### [tracing.py](./tracing.py)
Пример сценария, который генерирует трассировку, содержащую 
три именованных span-а: «foo», «bar» и «baz» (вывод выполняется в консоль):

> python tracing.py


### [jaeger-example.py](./jaeger-example.py)
Модифицированный пример для вывода трассировки в Jaeger.  
Перед выполнением скрипта следует запустить контейнер с Jaeger-ом командой:
> docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one  

запустить скрипт:
> python jaeger-example.py


После выполнения скрипта можно перейти по адресу  http://localhost:16686 для просмотра
трассировки. 


### [flask-example.py](./flask-example.py)
Пример трассировки сервиса на flask (вывод в консоль)

> python flask-example.py

### [flask-jaeger-example.py](./flask-jaeger-example.py)
Пример трассировки сервиса на flask (трассировка в Jaeger)

> python flask-example.py

### [metrics.py](./metrics.py)
Пример вывода метрик в консоль

> python metrics.py





