<template>
  <div class="upload-container">
    <h1>Image Processing App</h1>
    <form @submit.prevent="submitForm">
      <div>
        <label for="image">Select an Image:</label>
        <input type="file" id="image" @change="handleFileChange" />
      </div>
      <div>
        <label for="operation">Operation:</label>
        <select id="operation" v-model="operation">
          <option value="resize">Resize</option>
          <option value="grayscale">Grayscale</option>
          <option value="dmc-colors">Convert to DMC Colors</option>
          <option value="custom-dmc-colors">Recreate with Selected DMC Colors</option>
        </select>
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
    <div v-if="dmcCodes">
      <h2>DMC Colors Used:</h2>
      <div style="display: flex; flex-wrap: wrap;">
        <div v-for="(name, index) in dmcCodes" :key="index"
          style="display: flex; align-items: center; margin: 10px; width: 20%;">
          <span :style="{
            display: 'inline-block',
            width: '20px',
            height: '20px',
            backgroundColor: hexValues[index],
            marginRight: '10px'
          }"></span>
          {{ name }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

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

      const formData = new FormData();
      formData.append("file", this.file);
      try {
        if (this.operation === "dmc-colors") {
          formData.append("max_colors", this.maxColors);
          formData.append("image_width", this.imageWidth);
          formData.append("use_grid_filter", this.useGridFilter);
          const response = await axios.post("http://127.0.0.1:8000/dmc-colors/", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = `${response.data.image_url}?t=${Date.now()}`; // DMC-converted image w/ timestamp
          this.dmcCodes = response.data.dmc_codes; // List of DMC color codes
          this.hexValues = response.data.hex_values; // Corresponding hex values
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
          const response = await axios.post(
            "http://127.0.0.1:8000/custom-dmc-colors/",
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          );
          this.processedImage = response.data.image_url;
          this.dmcCodes = response.data.dmc_codes; // List of DMC color codes
          this.hexValues = response.data.hex_values; // Corresponding hex values
          this.selectedDmcColors = response.data.dmc_codes.map((code) => ({
            name: "Custom",
            code,
          }));
        } else {
          formData.append("operation", this.operation);
          const response = await axios.post("http://127.0.0.1:8000/process/", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = response.data.image_url;
          this.dmcCodes = null;
          this.hexValues = null;
        }
      } catch (error) {
        console.error("Error processing the image:", error);
        alert(error.response.data.detail);
      }
    },
  },
};
</script>

<style>
.upload-container {
  max-width: 90vw;
  margin: auto;

  text-align: center;
  align-items: center;
}

.processed-image {
  width: 60vw;
  max-height: 60vh;
  -ms-interpolation-mode: nearest-neighbor;
  object-fit: contain;
  margin: auto;
  display: block;
}

.input-hint {
  font-size: 0.8em;
  color: #666;
  margin-left: 8px;
}
</style>