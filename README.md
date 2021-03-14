# pipeline
Simple python program, that allows to create and run pipelines based on ~~yaml~~ json configurations

## how to run
chmod +x start
./start path_to_input_json

## how to use
call web server (default localhost:8000) end point /start_pipeline with post request and json body with key 'pipeline' and value - the name of pipeline you want to start and inputs as supplied in input json
example:
`curl 127.0.0.1:8000/start_pipeline -v -X POST -d '{"pipeline": "test_pipeline", "document_id": 1, "page_num": 2}'`
output will be the json with the id of your pipeline in key 'pipeline_id'
`{"pipeline_id": 1}`

check state of pipeline by calling webserver endpoint /get_pipeline_status with post request (even tho its called GET_pipeline_status..) with json body with key 'pipeline' and value of the id of your pipeline that you got when calling start_pipeline
`curl 127.0.0.1:8000/get_pipeline_state -v -X POST -d '{"pipeline_id": 1}'`
The return will be json with the state of pipeline under key 'state'
`{"state": "finished"}`

get pipeline outputs by calling endpoint `get_pipeline_outputs` with json body with key 'pipeline' and value of the id of your pipeline.
`curl 127.0.0.1:8000/get_pipeline_outputs -v -X POST -d '{"pipeline_id": 1}'`
output will be json with keys being your outputs supplied in input json and outputs being its values
`{"extractions": "todo: support json"}`



## input json example:
```
{
   "test_pipeline":{
      "name":"test pipeline",
      "inputs":[
         "document_id",
         "page_num"
      ],
      "outputs":[
         "extractions"
      ],
      "components":{
         "image_preprocessing":{
            "runner":"test_data.ImagePreprocessing",
            "inputs":[
               "document_id",
               "page_num"
            ],
            "outputs":[
               "page_id"
            ]
         },
         "image_ocr":{
            "runner":"test_data.OCRModel",
            "inputs":[
               "image_preprocessing.page_id"
            ],
            "outputs":[
               "page_id"
            ]
         },
         "extractor":{
            "runner":"test_data.ExtractionModel",
            "inputs":[
               "image_ocr.page_id"
            ],
            "outputs":[
               "extractions"
            ]
         }
      }
   }
}
```
compontents can also include key 'dependencies' with names of components that must be finished in order fot the component to start running
