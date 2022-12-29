# Copyright 2022 Matthew Nykamp All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from flask import Flask
from flask import request

from google.cloud import bigquery_storage_v1
from google.cloud.bigquery_storage_v1 import types
from google.cloud.bigquery_storage_v1 import writer
from google.protobuf import descriptor_pb2

import match_pb2

app = Flask(__name__)

def createRowFromRequest(request)
  row = match_pb2.MatchRecord()
  row.date = request.form['date']
  row.patch = request.form['patch']
  row.settings = request.form['settings']
  row.player = []

  for player in request.form["player"]:
    rowPlayer = match_pb2.PlayerRecord()
    rowPlayer.steamid = player.steamid
    rowPlayer.kills = player.kills
    rowPlayer.deaths = player.deaths
    rowPlayer.assists = player.assists
    rowPlayer.team = player.team
    rowPlayer.abilities = []

    for ability in player.abilities:
      playerAbility = match_pb2.AbilityRecord()
      playerAbility.name = ability.name
      playerAbility.level = ability.level

      rowPlayer.abilities.append(playerAbility)

    row.player.append(rowPlayer)

  return row

@app.route('/match', methods=['POST'])
def addMatch():

  project_id = 'website-project-1-256917'
  dataset_id = 'match_history'
  table_id = 'matches'

  write_client = bigquery_storage_v1.BigQueryWriteClient()
  parent = write_client.table_path(project_id, dataset_id, table_id)
  stream_name = f'{parent}/_default'

  request_template = types.AppendRowsRequest()
  request_template.write_stream = stream_name

  proto_schema = types.ProtoSchema()
  proto_descriptor = descriptor_pb2.DescriptorProto()
  customer_record_pb2.CustomerRecord.DESCRIPTOR.CopyToProto(proto_descriptor)
  proto_schema.proto_descriptor = proto_descriptor
  proto_data = types.AppendRowsRequest.ProtoData()
  proto_data.writer_schema = proto_schema
  request_template.proto_rows = proto_data

  append_rows_stream = writer.AppendRowsStream(write_client, request_template)

  row = createRowFromRequest(request)

  proto_rows = types.ProtoRows()
  proto_rows.serialized_rows.append(row.SerializeToString())

  request = types.AppendRowsRequest()
  proto_data = types.AppendRowsRequest.ProtoData()
  proto_data.rows = proto_rows
  request.proto_rows = proto_data

  future = append_rows_stream.send(request)
  future.result()

  append_rows_stream.close()

  return 'Success.', 200

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8080, debug=True)
