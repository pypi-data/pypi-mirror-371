import yaml
from pymusiclooper.audio import MLAudio


class SampleRateAnalyzer:
    file: str
    output: str

    def __init__(self, yaml_data: dict, output_path: str):

        self.file = yaml_data["File"]
        self.output = output_path


    def run(self) -> bool:

        print("Running sample rate analysis")

        sample_rate: int = 0
        duration: int = 0
        successful: bool
        error: str = ""

        try:
            audio_file = MLAudio(self.file)
            sample_rate = audio_file.rate
            duration = audio_file.total_duration
            successful = True
        except Exception as e:
            print("Error analyzing audio", e)
            successful = False
            error = str(e)

        data = dict(
            Successful=successful,
            Error=error,
            SampleRate=sample_rate,
            Duration=duration
        )

        try:
            with open(self.output, 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            return successful
        except Exception as e:
            print(e)
            return False
