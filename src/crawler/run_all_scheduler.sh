#filepath="./scheduler/"
#for filename in $filepath*; do
#    python $filename
#done

#python ./scheduler/download_opendata.py > /tmp/download_opendata.txt
#python ./scheduler/download_stock_buy_sell.py > /tmp/download_stock_buy_sell.txt
#python ./scheduler/download_stock_history.py > /tmp/download_stock_history.txt
#python ./scheduler/api_predict_prophet.py > /tmp/api_predict_prophet.txt

python ./scheduler/download_opendata.py
python ./scheduler/download_stock_buy_sell.py
python ./scheduler/download_stock_history.py
# python ./scheduler/api_predict_prophet.py
