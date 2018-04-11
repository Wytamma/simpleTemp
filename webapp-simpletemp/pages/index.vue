<template>
  <div>
    <v-btn color="primary" dark @click="initialise" class="mb-2">Refresh</v-btn>
    <v-btn color="primary" dark class="mb-2">Download</v-btn>
    <v-dialog v-model="dialog" max-width="500px">
      
      <v-card>
        <v-card-title>
          <span class="headline">Edit</span>
        </v-card-title>
        <v-card-text>
          <v-container grid-list-md>
            <v-layout wrap>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Descriptive Name" v-model="editedItem.name"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Max Temp" v-model="editedItem.max"></v-text-field>
              </v-flex>
              <v-flex xs12 sm6 md4>
                <v-text-field label="Min Temp" v-model="editedItem.min"></v-text-field>
              </v-flex>
            </v-layout>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" flat @click.native="close">Cancel</v-btn>
          <v-btn color="blue darken-1" flat @click.native="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-data-table
      :headers="headers"
      :items="items"
      hide-actions
      :loading="loading"
      class="elevation-1"
    >
      <v-progress-linear slot="progress" color="blue" indeterminate></v-progress-linear>
      <template slot="items" slot-scope="props">
        <td class="text-xs-center">{{ props.item.time }}</td>
        <td class="text-xs-center" ><b style="font-size: 28px">{{ props.item.temperature }}</b></td>
        <td class="text-xs-center">{{ props.item.name }}</td>
        <td class="text-xs-center">{{ props.item.max }}</td>
        <td class="text-xs-center">{{ props.item.min }}</td>
        <td class="text-xs-center">{{ props.item.probe_id }}</td>
        <td class="justify-center layout px-0">
          <v-btn icon class="mx-0" @click="editItem(props.item)">
            <v-icon color="teal">edit</v-icon>
          </v-btn>
        </td>
      </template>
      <template slot="no-data">
        <v-btn color="primary" @click="initialise">Reload</v-btn>
      </template>
    </v-data-table>
  </div>
</template>



<script>
import axios from 'axios';
const url = 'http://10.0.0.39:5000' //'http://0.0.0.0:5000' //localhost
export default {
  data: function () {
    return {
      headers: [
        {text: 'Time', value: 'time', align: 'center',},
        {text: 'Temperature (˚C)', value: 'temperature', align: 'center',},
        {text: 'Name', value: 'name', align: 'center',},
        {text: 'Max (˚C)', value: 'max', align: 'center',},
        {text: 'Min (˚C)', value: 'min', align: 'center',},
        {text: 'Probe id', value: 'probe_id', align: 'center',},
      ],
      dialog: false,
      interval: null,
      probes: [],
      errors: [],
      items: [],
      temperatures: [],
      loading: true,
      editedItem: {
        name: '',
        probe_id: '0',
        max: 0,
        min: 0,
        temperature: 0,
        time: ''
      },
      editedIndex: null
    }
  },
  created() {
    this.initialise()
    this.interval = setInterval(function () {
      this.updateTemps();
    }.bind(this), 5000); 
  },
  methods: {
    initialise () {
      // get probes
      this.items = []
      this.loading = true
      axios.get(url + '/probes')
      .then(response => {
        // JSON responses are automatically parsed.
        this.probes = response.data.data
        for (let i = 0; i < this.probes.length; i++) {
          let probe = this.probes[i];
          axios.get(url + '/records/' + probe.probe_id + '?limit=1')
          .then(response => {
            // JSON responses are automatically parsed.
            let recordItem = response.data.data[0]
            recordItem.max = probe.max
            recordItem.min = probe.min
            if (!probe.name) {
              probe.name = probe.probe_id
            }
            recordItem.name = probe.name
            this.items.push(recordItem)
            this.loading = false
          })
          .catch(e => {
            console.log(e);
            this.errors.push(e)
          })
        }
      })
      .catch(e => {
        console.log(e);
        this.errors.push(e)
      })
    },
    updateTemps () {
      this.loading = true
      for (let i = 0; i < this.items.length; i++) {
          let probe_id = this.items[i].probe_id;
          axios.get(url + '/records/' + probe_id + '?limit=1')
          .then(response => {
            // JSON responses are automatically parsed.
            this.items[i].temperature = response.data.data[0].temperature
            this.items[i].time = response.data.data[0].time
            this.loading = false
          })
          .catch(e => {
            console.log(e);
            this.errors.push(e)
          })
        }
    },
    editItem (item) {
      this.editedIndex = this.items.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },
    save () {
      Object.assign(this.items[this.editedIndex], this.editedItem)
      var params = new URLSearchParams();
      params.append('name', this.editedItem.name);
      params.append('max', this.editedItem.max);
      params.append('min', this.editedItem.min);
      params.append('probe_id', this.editedItem.probe_id);
      axios.put(url + '/probes?', params)
      .then(response => {
        // JSON responses are automatically parsed.
        console.log(response.data.message)
      })
      .catch(e => {
        console.log(e);
        this.errors.push(e)
      })
      this.close()
    },
    close () {
      this.dialog = false
    },
  },
  beforeDestroy: function(){
    clearInterval(this.interval);
  }
}
</script>

