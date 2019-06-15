#!/bin/bash
while :
do
cd /c/Users/CoCo\ Lab/Downloads/emotionFiles
startTime=`date +%s`
py -3 main.py
cd emoTxt
rm *.csv
cd ..
cp *.csv emoTxt
cd emoTxt
for file in *.csv
	do
	name=${file%%[.]*}
	sh classify.sh -i $name.csv -d sc -p -e anger
	sh classify.sh -i $name.csv -d sc -p -e fear
	sh classify.sh -i $name.csv -d sc -p -e joy
	sh classify.sh -i $name.csv -d sc -p -e sadness
	echo "Emotion intesity calculation succeed...."
	cd "classification_$name""_anger"
	mv predictions_anger.csv "$name""_prediction_anger.csv"
	mv "$name""_prediction_anger.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles
    cd ..sh
	rm -rf "classification_$name""_anger"
    cd "classification_$name""_fear"
	mv predictions_fear.csv "$name""_prediction_fear.csv"
	mv "$name""_prediction_fear.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles
    cd ..
	rm -rf "classification_$name""_fear"
    cd "classification_$name""_joy"
	mv predictions_joy.csv "$name""_prediction_joy.csv"
	mv "$name""_prediction_joy.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles
    cd ..
	rm -rf "classification_$name""_joy"
    cd "classification_$name""_sadness"
	mv predictions_sadness.csv "$name""_prediction_sadness.csv"
	mv "$name""_prediction_sadness.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles
	cd ..
	rm -rf "classification_$name""_sadness"
	cd /c/Users/CoCo\ Lab/Downloads/emotionFiles
	echo "Intensity files are transfered to emotionFiles Directory...."
	py -3 nrc.py $name
	echo "Insertion in InfluxDB Succeed...."
	mv "$name""_prediction_fear.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles/predictedBackup
	mv "$name""_prediction_anger.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles/predictedBackup
	mv "$name""_prediction_joy.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles/predictedBackup
	mv "$name""_prediction_sadness.csv" /c/Users/CoCo\ Lab/Downloads/emotionFiles/predictedBackup
	echo "Intensity files are transfered into backup folder...."
	rm $name.csv
	rm "$name""_data.txt"
	cd emoTxt
	rm $name.csv
	echo "Next Computation....!!!"
	done
endTime=`date +%s`
let diffTime=(endTime-startTime)
let sleepTime=86400-diffTime
echo "Sleeping for one day...."
sleep sleepTime
cd /c/Users/CoCo\ Lab/Downloads/emotionFiles
rm *.txt
rm *.csv
done