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
      <div>
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
      <div v-if="operation === 'custom-dmc-colors'">
        <h3>Selected DMC Colors</h3>
        <ul>
          <li v-for="(color, index) in selectedDmcColors" :key="index">
            {{ color.name }} (Code: {{ color.code }})
            <button type="button" @click="removeDmcColor(index)">Remove</button>
          </li>
        </ul>
        <div>
          <label for="newDmcColor">Add DMC Color Code:</label>
          <input type="text" id="newDmcColor" v-model="newDmcColor" />
          <button type="button" @click="addDmcColor">Add</button>
        </div>
      </div>
      <button type="submit">Process Image</button>
    </form>
    <div v-if="processedImage">
      <h2>Processed Image:</h2>
      <img :src="processedImage" alt="Processed" class="processed-image" />
    </div>
    <div v-if="dmcCodes" class="dmc-colors-container">
      <h2>DMC Colors Used:</h2>
      <div class="dmc-colors-grid">
        <div v-for="(name, index) in dmcCodes" 
             :key="index"
             class="dmc-color-item">
          <div class="color-square"
               :style="{
                 backgroundColor: hexValues[index]
               }">
          </div>
          <div class="color-info">
            DMC-{{ name }} 
            <span v-if="colorCounts">(x{{ colorCounts[index] }})</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { config } from "../config";

export default {
  data() {
    return {
      file: null,
      operation: "resize",
      processedImage: null,
      dmcColors: null,
      selectedDmcColors: [],
      newDmcColor: "",
      maxColors: 10,
      imageWidth: 100,
      useGridFilter: false,
      operations: [
        { value: 'resize', label: 'Resize' },
        { value: 'grayscale', label: 'Grayscale' },
        { value: 'dmc-colors', label: 'DMC Colors' },
        { value: 'custom-dmc-colors', label: 'Custom DMC Colors' }
      ],
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    addDmcColor() {
      // Replace this with actual validation for DMC codes if needed
      if (this.newDmcColor.trim() === "") return;
      const existing = this.selectedDmcColors.find(
        (color) => color.code === this.newDmcColor
      );
      if (!existing) {
        this.selectedDmcColors.push({ name: "Custom", code: this.newDmcColor });
        this.newDmcColor = "";
      }
    },
    removeDmcColor(index) {
      this.selectedDmcColors.splice(index, 1);
    },
    async submitForm() {
      if (!this.file) {
        alert("Please select a file.");
        return;
      }
      // Clear the previous processed image
      this.processedImage = null;
      this.dmcCodes = null;
      this.hexValues = null;
      this.colorCounts = null;

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
          this.selectedDmcColors = response.data.dmc_codes.map((code) => ({
            name: "Custom",
            code,
          }));
        } else if (this.operation === "custom-dmc-colors") {
          if (this.selectedDmcColors.length === 0) {
            alert("Please add at least one DMC color code.");
            return;
          }
          formData.append("max_colors", this.maxColors);
          formData.append("image_width", this.imageWidth);
          formData.append("use_grid_filter", this.useGridFilter);
          formData.append("dmc_colors", this.selectedDmcColors.map((color) => color.code).join(","));
          const selectedDmcCodes = this.selectedDmcColors.map((color) => color.code);
          const response = await axios.post(`${config.apiUrl}/custom-dmc-colors`, formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
          this.processedImage = `${response.data.image_url}?t=${Date.now()}`; // DMC-converted image w/ timestamp
          this.dmcCodes = response.data.dmc_codes; // List of DMC color codes
          this.hexValues = response.data.hex_values; // Corresponding hex values
          this.colorCounts = response.data.color_counts; // Number of times each DMC color is used
          this.selectedDmcColors = response.data.dmc_codes.map((code) => ({
            name: "Custom",
            code,
          }));
        } else {
          formData.append("operation", this.operation);
          const response = await axios.post(`${config.apiUrl}/process`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = response.data.image_url;
          this.dmcCodes = null;
          this.hexValues = null;
          this.colorCounts = null;
        }
      } catch (error) {
        console.error("Error:", error);
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
  margin-top: 2rem;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.dmc-colors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  padding: 1rem;
  width: 100%;
}

.dmc-color-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.color-square {
  width: 2rem;
  height: 2rem;
  min-width: 2rem;  /* Ensure square shape */
  margin-right: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.color-info {
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

.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.color-box {
  position: relative;
  aspect-ratio: 1;
}

.color-preview {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.no-color {
  background: rgba(255, 255, 255, 0.05);
}

.question-mark {
  font-size: 1.5rem;
  opacity: 0.5;
}

.dmc-code {
  position: absolute;
  bottom: 4px;
  font-size: 0.8rem;
  background: rgba(0, 0, 0, 0.5);
  padding: 2px 6px;
  border-radius: 4px;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(255, 0, 0, 0.8);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  line-height: 1;
}

.remove-btn:hover {
  background: rgba(255, 0, 0, 1);
}

.color-input {
  display: flex;
  gap: 0.5rem;
}

.color-input input {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: inherit;
}

.color-input button {
  padding: 0.5rem 1rem;
  background: #42b883;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

.color-input button:hover {
  background: #3aa876;
}
</style>