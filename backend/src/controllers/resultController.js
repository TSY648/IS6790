import { saveLevelResult } from "../services/resultService.js";

export async function createResult(req, res, next) {
  try {
    const result = await saveLevelResult(req.body);
    res.json(result);
  } catch (error) {
    next(error);
  }
}
