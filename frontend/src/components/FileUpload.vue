<template>
  <div class="upload-container">
    <h1>Select an Operation</h1>
    
    <!-- Navigation Bar -->
    <nav class="nav-tabs">
      <button 
        v-for="op in operations" 
        :key="op.value"
        :class="['nav-tab', { active: operation === op.value }]"
        @click="operation = op.value"
      >
        {{ op.label }}
      </button>
    </nav>

    <form @submit.prevent="submitForm">
      <div v-if="operation !== 'visualize'">
        <label for="image">Select an Image:</label>
        <input type="file" id="image" @change="handleFileChange" />
      </div>
      <div v-if="operation === 'dmc-colors' || operation === 'custom-dmc-colors'">
        <label for="colorCount">Maximum # of Colors:</label>
        <input 
          type="number" 
          id="colorCount" 
          v-model.number="maxColors" 
          min="2" 
          max="50" 
          step="1"
        />
        <span class="input-hint">(2-50 colors)</span>
      </div>
      <div v-if="operation === 'dmc-colors' || operation === 'custom-dmc-colors'">
        <label for="Image width">Cross-stitch image width (in pixels)</label>
        <input type="number" id="imageWidth" v-model.number="imageWidth" min="5" max="1000" step="1" />
        <span class="input-hint">(Use this to make the image more pixelated)</span>
      </div>
      <div v-if="operation === 'dmc-colors' || operation === 'custom-dmc-colors'">
        <label for="useGridFilter">Use Grid Filter</label>
        <input type="checkbox" id="useGridFilter" v-model="useGridFilter" />
        <span class="input-hint">(Remove grid lines)</span>
      </div>
      <div v-if="dmcCodes.length > 0" class="dmc-colors-container">
        <h2>DMC Colors Used:</h2>
        <div v-if="operation === 'custom-dmc-colors'" class="color-input">
          <input type="text" v-model="newDmcColor" placeholder="Enter the DMC color code" />
          <button type="button" @click="addDmcColor">Add</button>
        </div>
        <div class="dmc-colors-grid">
          <div v-for="(name, index) in dmcCodes" 
            :key="index"
            class="dmc-color-item">
          <button v-if="operation === 'custom-dmc-colors'"
            class="remove-color-btn"
            @click.prevent="removeDmcColor(index)"
            title="Remove color"
            >x</button>
          <div class="color-square"
            :class="{ 'no-color': !hexValues[index] }"
            :style="{
              backgroundColor: hexValues[index] || 'transparent'
            }">
            <span v-if="!hexValues[index]" class="question-mark">?</span>
          </div>
          <div class="color-info">
            DMC-{{ name }} 
            <span v-if="colorCounts">(x{{ colorCounts[index] }})</span>
          </div>
          </div>
        </div>
      </div>
      <button v-if="operation !== 'visualize'" type="submit">Process Image</button>
    </form>
    <div v-if="processedImage && operation === 'visualize'">
      <GridVisualization 
        :imageUrl="processedImage" 
        :pixelWidth="imageWidth" 
      />
    </div>
    <div v-else-if="processedImage">
      <h2>Processed Image:</h2>
      <img :src="processedImage" alt="Processed" class="processed-image" />
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { config } from "../config";
import GridVisualization from "./GridVisualization.vue";

export default {
  components: {
    GridVisualization
  },
  data() {
    return {
      file: null,
      operation: "resize",
      processedImage: null,
      dmcColors: null,
      dmcCodes: [],
      hexValues: [],
      colorCounts: [],
      newDmcColor: "",
      maxColors: 10,
      imageWidth: 100,
      useGridFilter: false,
      operations: [
        { value: 'resize', label: 'Resize' },
        { value: 'grayscale', label: 'Grayscale' },
        { value: 'dmc-colors', label: 'DMC Colors' },
        { value: 'custom-dmc-colors', label: 'Custom DMC Colors' },
        { value: 'visualize', label: 'Visualize' }
      ],
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    addDmcColor() {
      if (this.newDmcColor.trim() === "") return;
      const existing = this.dmcCodes.includes(this.newDmcColor);
      if (!existing) {
        this.dmcCodes.push(this.newDmcColor);
        this.hexValues.push(0);
        this.colorCounts.push(0);
        this.newDmcColor = "";
      }
    },
    removeDmcColor(index) {
      this.dmcCodes.splice(index, 1);
      this.hexValues.splice(index, 1);
      this.colorCounts.splice(index, 1);
    },
    async submitForm() {
      if (!this.file) {
        alert("Please select a file.");
        return;
      }
      // Clear the previous processed image
      this.processedImage = null;

      const formData = new FormData();
      formData.append("file", this.file);
      try {
        if (this.operation === "dmc-colors") {
          formData.append("max_colors", this.maxColors);
          formData.append("image_width", this.imageWidth);
          formData.append("use_grid_filter", this.useGridFilter);
          const response = await axios.post(`${config.apiUrl}/dmc-colors`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = `${response.data.image_url}?t=${Date.now()}`; // DMC-converted image w/ timestamp
          this.dmcCodes = response.data.dmc_codes; // List of DMC color codes
          this.hexValues = response.data.hex_values; // Corresponding hex values
          this.colorCounts = response.data.color_counts; // Number of times each DMC color is used
        } else if (this.operation === "custom-dmc-colors") {
          if (this.dmcCodes.length === 0) {
            alert("Please add at least one DMC color code.");
            return;
          }
          formData.append("max_colors", this.maxColors);
          formData.append("image_width", this.imageWidth);
          formData.append("use_grid_filter", this.useGridFilter);
          formData.append("dmc_colors", this.dmcCodes.join(","));
          const response = await axios.post(`${config.apiUrl}/custom-dmc-colors`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          this.processedImage = `${response.data.image_url}?t=${Date.now()}`; // DMC-converted image w/ timestamp
          this.dmcCodes = response.data.dmc_codes; // List of DMC color codes
          this.hexValues = response.data.hex_values; // Corresponding hex values
          this.colorCounts = response.data.color_counts; // Number of times each DMC color is used
        } else if (this.operation === 'visualize') {
          // Use the original image directly
          const reader = new FileReader();
          reader.onload = (e) => {
            this.processedImage = e.target.result;
          };
          reader.readAsDataURL(this.file);
          this.dmcCodes = [];
          this.hexValues = [];
          this.colorCounts = [];
        } else {
          formData.append("operation", this.operation);
          const response = await axios.post(`${config.apiUrl}/process`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = response.data.image_url;
          this.dmcCodes = [];
          this.hexValues = [];
          this.colorCounts = [];
        }
      } catch (error) {
        console.error("Error:", error);
        console.error("Error details:", {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message
        });
        alert(error.response?.data?.detail || "An error occurred");
      }
    },
  },
};
</script>

<style scoped>
.upload-container {
  width: 100%;
  box-sizing: border-box;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (min-width: 768px) {
  .form-group {
    flex-direction: row;
    align-items: center;
  }
  
  .form-group label {
    min-width: 200px;
    text-align: right;
  }
}

.input-hint {
  font-size: 0.8em;
  color: #666;
  margin-left: 0.5rem;
}

.processed-image {
  max-width: 90vw;
  max-height: 70vh;
  object-fit: contain;
  margin: auto;
  display: block;
}

.dmc-colors-container {
  width: 100%;
  max-width: 60rem;
  margin: 0 auto;
  background-color: rgba(255, 255, 255, 0.05);
  padding: 1rem;
}

.remove-color-btn {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  width: 1.25rem;
  height: 1.25rem;
  background: rgba(255, 0, 0, 0.8);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.remove-color-btn:hover {
  background: rgba(255, 0, 0, 1);
}

.dmc-colors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(8rem, 1fr));
  gap: 1rem;
  padding: 1rem;
  width: 100%;
}

.dmc-color-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  border-radius: 0.25rem;
  background: rgba(255, 255, 255, 0.05);
}

.color-square {
  width: 4rem;
  height: 4rem;
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
}

.color-info {
  font-size: 0.875rem;
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0 1rem;
}

.nav-tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav-tab:hover {
  background: rgba(255, 255, 255, 0.05);
}

.nav-tab.active {
  border-bottom-color: #42b883;
  background: rgba(66, 184, 131, 0.1);
}

.no-color {
  background: rgba(255, 255, 255, 0.05);
}

.question-mark {
  font-size: 2.5rem;
  opacity: 0.5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-input {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0 1rem;
  width: 100%;
  max-width: 30rem;
  margin: 0 auto 1rem auto;
}

.color-input input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.25rem;
  background: rgba(255, 255, 255, 0.05);
  color: inherit;
  font-size: 1rem;
}

.color-input button {
  padding: 0.5rem 1rem;
  background: #42b883;
  border: none;
  border-radius: 0.25rem;
  color: white;
  cursor: pointer;
  font-size: 1rem;
}

.color-input button:hover {
  background: #3aa876;
}
</style>