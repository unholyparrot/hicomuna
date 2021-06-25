# Hicomuna

Приложение для ввода данных мониторинга пациентов.

## Последнее обновление

Добавлены уведомления при возникновении ошибки создания / открытия файла.

## Требования

Необходимые пакеты перечислены в [requirements.txt](./requirements.txt "требования").

## Самостоятельная сборка исполняемого файла

```bash
$ git clone https://github.com/unholyparrot/hicomuna.git
$ cd monitowl-agent
$ pip install -r requirements.txt
$ pip install pyinstaller
$ pyinstaller hicomuna.spec
```

Исполняемый файл `hicomuna.exe` будет в директории *dist/hicomuna*. В директории *dist/hicomuna/example_data*
находятся примеры файлов для записи данных.

## Настройка отображения

* Настройка отображения серий данных производится в разделе **Plot :: PointsStyle** файла *configs.json*.
Ключевые слова можно посмотреть 
[здесь](https://pyqtgraph.readthedocs.io/en/latest/graphicsItems/plotdataitem.html?highlight=PlotDataItem 
"PlotDataItem description").

* Настройка отображения типов добавляемых категорий возможна, но нужно редактировать код виджета, так как помимо 
самой категории необходимо добавлять правило обработки данных. 
  
* Настройка отображения типов событий производится в разделе **InputDialog :: Events :: Enum**, в поле 
**InputDialog :: Events :: Default** можно указать индекс значения из **Enum**, отображаемого по умолчанию.
  
* Аналогичным образом производится настройка отображаемой кратности введения препарата.
