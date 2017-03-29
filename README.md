# Бекенд для проекта "Нейронные сети в искусстве"

В данном репозитории находится реализация Rest API, позволяющего принимать картинку, картинку со стилем и возвращать обработанную картинку.

API поддерживает следующие запросы:

| Метод  | Адрес                        | Описание                                                                                                                                                                                                                                                                      |
|--------|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| POST   | /api/image                   | Помещает увртинку в очередь обработки. Требует два изображения: художественный стиль (в формате jpg, название поля style) и изображение для обработки (формат jpg, поле subject). Возвращает json ответ вида {'success': True, 'id': id}, где id - идентификатор изображения. |
| DELETE | /api/image/\<image_id>        | Удаляет картинку с идентификатором \<image_id> из очереди обработки.                                                                                                                                                                                                           |
| GET    | /api/image/\<image_id>        | Если картинка успешно обработана, то возвращается результат обработки, иначе возвращается ошибка 404.                                                                                                                                                                         |
| GET    | /api/image/\<image_id>/status | Возвращает json ответ, описывающий текущий статус картинки: она находится в очереди, обрабатывается алгоритмом и обработанный % либо обработка завершена.|                                                                                                                                                                                                                                   |

Для обработки запросов используется Flask, для реализации обработки изображений фреймворк [DeepPy](http://andersbll.github.io/deeppy-website/), картинки обрабатываются алгоритмом, описанным в статье [A Neural Algorithm of Artistic Style](https://arxiv.org/abs/1508.06576).
Реализация алгоритма взята из проекта [Neural Artistic Style in Python](https://github.com/andersbll/neural_artistic_style). 
## Примеры работы

<p align="center">
<b>Картинка:</b>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/tuebingen.jpg?raw=true" width="30%" align="top"/>
<b>Стиль:</b>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/starry_night.jpg?raw=true" width="30%" align= "top"/>
</p>

**Результат работы**
<p align="center">
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/tuebingen-starry_night.jpg?raw=true" width="30%"/>
</p>

**Картинка**
<p align="center">
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/margrethe.jpg?raw=true" width="20%"/>
</p>

**Стили**
<p align="center">
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/lundstroem.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/donelli.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/picasso.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/groening.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/skrik.jpg?raw=true" width="18%"/>
</p>

**Результаты**
<p align="center">
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/margrethe_lundstroem.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/margrethe_donelli.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/margrethe_picasso.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/margrethe_groening.jpg?raw=true" width="18%"/>
<img src="https://github.com/andersbll/neural_artistic_style/blob/master/images/margrethe_skrik.jpg?raw=true" width="18%"/>
</p>
