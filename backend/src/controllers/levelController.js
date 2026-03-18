import { getAllLevels, getLevelById } from "../services/levelService.js";

export async function listLevels(req, res, next) {
  try {
    const data = await getAllLevels();
    res.json({ success: true, data });
  } catch (error) {
    next(error);
  }
}

export async function getLevel(req, res, next) {
  try {
    const data = await getLevelById(req.params.levelId);
    res.json({ success: true, data });
  } catch (error) {
    next(error);
  }
}
