## Технические характеристики оборудования, на котором проводился эксперимент:

* CPU - AMD Ryzen 7 6800H
* RAM - 16 GB @ 6400Mhz
* Операционная система - EndeavourOS
* Python 3.11.8, numpy 1.26.4, linalg 1.0.4

## Эксперимент

### Алгоритмы:
* numpy - ```numpy.linalg.svd```
* simple (power method) - https://www.jeremykun.com/2016/05/16/singular-value-decomposition-part-2-theorem-proof-algorithm/
* advanced (jacobi method) - https://github.com/zlliang/jacobi-svd/blob/master/presentation.pdf



| Алгоритм | Сжатие x2 | Время работы (сек.) |
| --- | --- | --- |
| numpy | <img src="captchas/numpy.bmp" width="250px"> | 2 |
| simple | <img src="captchas/simple.bmp" width="250px"> | 3148
| advanced | <img src="captchas/jacobi.bmp" width="250px"> | 669 |


При внимательном изучении "разжатых" картинок заметных различий найдено не было. 


Рассмотрим картинку такую, что её матрица неплотная.


| Алгоритм | Сжатие x10 | Время работы (сек.) |
| --- | --- | --- |
| numpy | <img src="rainbow/numpy.bmp" width="250px"> | 0.14 |
| simple | <img src="rainbow/simple.bmp" width="250px"> | 302 |
| advanced | <img src="rainbow/jacobi.bmp" width="250px"> | 40 |

Однако и здесь не было замечено разницы между разными алгоритмами. Увы.