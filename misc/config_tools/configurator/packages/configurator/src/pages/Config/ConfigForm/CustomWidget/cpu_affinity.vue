<template>
  <div style="border:1px solid gray;background: #F5F5F5;padding: 1rem">
    <b>{{ uiOptions.title }}</b>
    <div class="p-4">
      <div v-if="defaultVal.pcpu && defaultVal.pcpu.length>0">
        <b-row>
          <b-col></b-col>
          <b-col></b-col>
          <b-col>Virtual CPU ID</b-col>
          <b-col class="ps-5">Real-time vCPU:</b-col>
          <b-col></b-col>
        </b-row>
        <b-row class="align-items-center"
               v-for="(cpu,index) in defaultVal.pcpu">
          <b-col>
            <span v-if="index===0" style="color: red; margin-left: -10px;margin-right: 4px">*</span>
            pCPU ID
          </b-col>
          <b-col>
            <b-form-select :state="validateCPUAffinity(cpu.pcpu_id)" v-model="cpu.pcpu_id"
                           :options="pcpuid_enum"></b-form-select>
            <b-form-invalid-feedback>
              pCPU ID is required!
            </b-form-invalid-feedback>
          </b-col>
          <b-col class="p-3 col-3">
            <div style="padding:9px;border-radius: 9px;width: 100%;border: 1px solid dimgray;background: lightgray;">
              {{ vCPUName(index) }}
            </div>
          </b-col>
          <b-col class="p-3">
            <b-form-checkbox v-model="cpu.real_time_vcpu" :value="'y'" :uncheckedValue="'n'" :disabled="!isRTVM"/>
          </b-col>
          <b-col>
            <div class="ToolSet">
              <div @click="addPCPU(index)" :class="{'d-none': (this.defaultVal.pcpu.length-1)!==index}">
                <Icon size="18px">
                  <Plus/>
                </Icon>
              </div>
              <div @click="removePCPU(index)">
                <Icon size="18px">
                  <Minus/>
                </Icon>
              </div>
            </div>
          </b-col>
        </b-row>
      </div>
      <b-row v-else>
        <b-col>
          <div class="ToolSet">
            <div @click="addPCPU(-1)">
              <Icon size="18px">
                <Plus/>
              </Icon>
            </div>
          </div>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import {
  fieldProps,
  vueUtils,
  formUtils,
  schemaValidate
} from '@lljj/vue3-form-naive';
import _ from 'lodash'
import {Icon} from "@vicons/utils";
import {Plus, Minus} from '@vicons/fa'
import {BFormInput, BRow} from "bootstrap-vue-3";

export default {
  name: "cpu_affinity",
  components: {BRow, BFormInput, Icon, Plus, Minus},
  props: {
    ...fieldProps,
  },
  watch: {
    rootFormData: {
      handler(newValue, oldValue) {
        this.defaultVal = vueUtils.getPathVal(newValue, this.curNodePath)
      },
      deep: true
    },
    defaultVal: {
      handler(newValue, oldValue) {
        vueUtils.setPathVal(this.rootFormData, this.curNodePath, newValue);
      },
      deep: true
    }
  },
  computed: {
    isRTVM() {
      return vueUtils.getPathVal(this.rootFormData, 'vm_type') === 'RTVM'
    },
    pcpuid_enum() {
      return window.getCurrentFormSchemaData().BasicConfigType.definitions.CPUAffinityConfiguration.properties.pcpu_id.enum
    },
    uiOptions() {
      return formUtils.getUiOptions({
        schema: this.schema,
        uiSchema: this.uiSchema
      });
    },
  },
  data() {
    return {
      defaultVal: vueUtils.getPathVal(this.rootFormData, this.curNodePath)
    }
  },
  mounted() {
    if (!_.isArray(this.defaultVal.pcpu)) {
      this.defaultVal.pcpu = []
      this.addPCPU(-1)
    }
  },
  methods: {
    validateCPUAffinity(pcpu_id) {
      return _.isNumber(pcpu_id) && this.pcpuid_enum.indexOf(pcpu_id) >= 0
    },
    vCPUName(index) {
      return `${this.rootFormData.name} vCPU ${index}`
    },
    addPCPU(index) {
      this.defaultVal.pcpu.splice(index + 1, 0, {pcpu_id: null, real_time_vcpu: "n"})
    },
    removePCPU(index) {
      if (this.defaultVal.pcpu.length === 1) {
        // prevent delete for the last one
        return
      }
      this.defaultVal.pcpu.splice(index, 1)
    }
  }
}
</script>

<style scoped>

.ToolSet {
  display: flex;
  justify-content: end;
  gap: 0.5rem;
  max-width: 5rem;
  width: 100%;
}

.ToolSet div {
  cursor: pointer;
  border: 1px solid gray;
  border-radius: 3px;
  background: #f9f9f9;
  padding: 5px 5px 3px;
}
</style>
