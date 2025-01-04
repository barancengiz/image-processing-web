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
        </select>
      </div>
      <button type="submit">Process Image</button>
    </form>
    <div v-if="processedImage">
      <h2>Processed Image:</h2>
      <img :src="processedImage" alt="Processed" />
    </div>
    <div v-if="dmcColors">
      <h2>DMC Colors Used:</h2>
      <ul>
        <li v-for="(name, code) in dmcColors" :key="code">
          {{ name }}
        </li>
      </ul>
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
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
    },
    async submitForm() {
      if (!this.file) {
        alert("Please select a file.");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.file);
      formData.append("operation", this.operation);

      try {
        if (this.operation === "dmc-colors") {
          const response = await axios.post("http://127.0.0.1:8000/dmc-colors/", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = response.data.image_url; // DMC-converted image
          this.dmcColors = response.data.dmc_colors; // List of DMC colors
        } else {
          formData.append("operation", this.operation);
          const response = await axios.post("http://127.0.0.1:8000/process/", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });
          this.processedImage = response.data.image_url;
          this.dmcColors = null;
        }
      } catch (error) {
        console.error("Error processing the image:", error);
        alert("Failed to process the image.");
      }
    },
  },
};
</script>

<style>
.upload-container {
  max-width: 500px;
  margin: auto;
  text-align: center;
}
</style>