<template>
  <header>
    <div>
      <w-icon class="icon" md color="secondary">
        mdi mdi-network-pos
      </w-icon>
      Lan Index
    </div>

    <div>
      <w-button @click="refreshScan" style="margin-right: 10px;">
        <w-icon color="secondary">
          mdi mdi-refresh
        </w-icon>
      </w-button>

      <w-button @click="downloadDatabase" style="margin-right: 10px;">
        <w-icon color="secondary">
          mdi mdi-table-arrow-down
        </w-icon>
      </w-button>

      <w-button @click="$refs.dbupload.click()" style="margin-right: 10px;">
        <w-icon color="secondary">
          mdi mdi-file-restore-outline
        </w-icon>
      </w-button>

      <input @change="handleDBUpload" ref="dbupload"style="display: none;" type="file">

    </div>
  </header>

  <w-drawer v-model="currentMac">
    <w-button @click="currentMac = null" style="position: absolute; top: 5px; right: 5px;" class="ma1" bg-color="error"
      icon="wi-cross"></w-button>
    <div id="editDrawer">
      <w-form v-model="editValid">
        <h3 style="margin-bottom: 30px;">Edit Host Info:</h3>

        <w-input v-model="editName" label="Name" :validators="[validators.required]">
        </w-input>

        <w-autocomplete @item-select="setEditIcon" class="mt3" label="Icon" :validators="[validators.required]"
          :items="aviableIcons">
        </w-autocomplete>

        <div style="display: flex; justify-content: center;">
          <w-icon class="icon" xl color="primary">
            mdi mdi-{{ editIcon }}
          </w-icon>
        </div>

        <div class="text-right mt6">
          <w-button type="submit" @click="saveMetadata" :disabled="editValid === false || editIcon == null">
            Save
          </w-button>
        </div>
      </w-form>
    </div>
  </w-drawer>

  <main>
    <w-spinner v-if="hosts.length == 0"
      style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);" />
    <div class="item" v-bind:class="{ 'offline-gray': h.online === false }" v-for="h in hosts">
      <div>
        <w-icon class="icon" xl color="primary">
          mdi mdi-{{ h.icon }}
        </w-icon>
      </div>
      <div class="item-text">
        <div>{{ h.name }}</div>
        <div>{{ h.ip }}</div>
        <div>{{ h.mac.toUpperCase() }}</div>
        <div style="text-overflow: ellipsis; overflow: hidden;">{{ h.manufacturer }}</div>
      </div>

      <w-button @click="currentMac = h.mac" style="margin-left: 10px;">
        <w-icon color="secondary">
          mdi mdi-tag-edit-outline
        </w-icon>
      </w-button>
    </div>
  </main>
</template>

<script>
export default {
  data() {
    return {
      currentMac: null,
      editName: null,
      editIcon: null,
      validators: {
        required: value => !!value || 'This field is required'
      },
      editValid: false,
      aviableIcons: [],
      hosts: []
    }
  },
  async mounted() {
    let r = await fetch('icons.json');
    this.aviableIcons = (await r.json()).map(e => { return { value: e, label: e, searchable: e } });
    this.refreshScan();
  },
  methods: {
    async refreshScan() {
      this.hosts = [];
      let r = await fetch('/api/scan');
      this.hosts = await r.json();
    },
    setEditIcon(e) {
      this.editIcon = e.value;
    },
    async saveMetadata() {
      let r = await fetch('/api/set-metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          'mac': this.currentMac,
          'name': this.editName,
          'icon': this.editIcon
        })
      });
      if (r.status == 200) {
        this.currentMac = null;
        this.editName = null;
        this.editIcon = null;
        this.refreshScan();
      } else {
        alert('An error occurred while saving the metadata');
      }
    },
    async downloadDatabase() {
      const anchor = document.createElement('a');
      anchor.href = '/api/get-db';
      anchor.download = 'lan-index.db';

      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
    },
    async handleDBUpload(event) {
      const file = event.target.files[0];
      let data = new FormData();
      data.append('db', file);
      fetch('/api/upload-db', {
        method: 'POST',
        body: data
      })
      .then(r => {
        this.refreshScan();
      })
      .catch(e => {
        alert('An error occurred while restoring the database');
      });
    }
  }
}
</script>
