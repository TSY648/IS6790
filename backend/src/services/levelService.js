import path from "path";
import { fileURLToPath } from "url";
import { pool } from "../config/db.js";
import { readJsonFile } from "../utils/readJson.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const levelsDir = path.resolve(__dirname, "../../levels");

export async function getAllLevels() {
  const [rows] = await pool.execute(
    `
    SELECT level_code, title, difficulty, sort_order
    FROM levels
    WHERE is_active = 1
    ORDER BY sort_order ASC
    `
  );

  return rows.map((row) => ({
    levelId: row.level_code,
    title: row.title,
    difficulty: row.difficulty,
    order: row.sort_order
  }));
}

export async function getLevelById(levelId) {
  const [rows] = await pool.execute(
    `
    SELECT level_code, config_file
    FROM levels
    WHERE level_code = ? AND is_active = 1
    LIMIT 1
    `,
    [levelId]
  );

  if (rows.length === 0) {
    const error = new Error("Level not found");
    error.statusCode = 404;
    throw error;
  }

  const configFile = rows[0].config_file;
  const fullPath = path.join(levelsDir, configFile);

  return readJsonFile(fullPath);
}
