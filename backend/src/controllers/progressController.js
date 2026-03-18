import { getProgress, saveProgress } from "../services/progressService.js";

export async function upsertProgress(req, res, next) {
  try {
    const result = await saveProgress(req.body);
    res.json(result);
  } catch (error) {
    next(error);
  }
}

export async function fetchProgress(req, res, next) {
  try {
    const result = await getProgress(req.params.userId);
    res.json({ success: true, data: result });
  } catch (error) {
    next(error);
  }
}
