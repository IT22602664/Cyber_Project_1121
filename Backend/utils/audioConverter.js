import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs';

const execPromise = promisify(exec);

/**
 * Convert audio file to WAV format using ffmpeg
 * @param {string} inputPath - Path to input audio file
 * @param {string} outputPath - Path to output WAV file (optional)
 * @returns {Promise<string>} - Path to converted WAV file
 */
export async function convertToWav(inputPath, outputPath = null) {
  try {
    // Generate output path if not provided
    if (!outputPath) {
      const dir = path.dirname(inputPath);
      const basename = path.basename(inputPath, path.extname(inputPath));
      outputPath = path.join(dir, `${basename}_converted.wav`);
    }

    // Check if ffmpeg is available
    try {
      await execPromise('ffmpeg -version');
    } catch (error) {
      console.warn('ffmpeg not found, skipping conversion');
      return inputPath; // Return original file if ffmpeg not available
    }

    // Convert to WAV: mono, 16kHz, 16-bit PCM
    const command = `ffmpeg -i "${inputPath}" -ar 16000 -ac 1 -sample_fmt s16 -y "${outputPath}"`;
    
    await execPromise(command);
    
    console.log(`✓ Audio converted: ${inputPath} -> ${outputPath}`);
    
    // Delete original file
    if (fs.existsSync(inputPath)) {
      fs.unlinkSync(inputPath);
    }
    
    return outputPath;
  } catch (error) {
    console.error('Error converting audio:', error.message);
    // Return original path if conversion fails
    return inputPath;
  }
}

/**
 * Convert multiple audio files to WAV format
 * @param {string[]} inputPaths - Array of input audio file paths
 * @returns {Promise<string[]>} - Array of converted WAV file paths
 */
export async function convertMultipleToWav(inputPaths) {
  const convertedPaths = [];
  
  for (const inputPath of inputPaths) {
    const convertedPath = await convertToWav(inputPath);
    convertedPaths.push(convertedPath);
  }
  
  return convertedPaths;
}

/**
 * Check if file is already in WAV format
 * @param {string} filePath - Path to audio file
 * @returns {boolean} - True if file is WAV
 */
export function isWavFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ext === '.wav';
}

