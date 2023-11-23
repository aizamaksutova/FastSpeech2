# FastSpeech2
Project on text-to-speech. This rep contains my implementation of FastSpeech2 model and all the steps to reimplement the pipeline

## Architecture
![](https://github.com/aizamaksutova/FastSpeech2/blob/main/assets/fastspeech2_arch.png)

### Data download
To download the LjSpeech dataset, Waveglow model, alignments and mels run the following command

```
./prepare_data.sh
```
If you have any issues with files asking you to access the files later try using simple scp from local computer to server

### Run inference
After you have downloaded all the necessary data, make sure to run inference with this command

```
python3 test.py -c hw_tts/configs/final_config.json -r final_model.pth -f inference.txt
```
The target texts are in the inference.txt file
