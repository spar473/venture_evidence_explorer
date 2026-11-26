const stopWords = new Set(
  "about also among and announced as at before by can case company described developed during early each first for from has have how in into its later new of on or reported research second some team than that the their them this through to under use used using venture was were when which who will with would year".split(
    " ",
  ),
);

export function ventureTokens(text: string) {
  return (
    text
      .toLowerCase()
      .normalize("NFKD")
      .match(/[a-z]{3,}/g) ?? []
  ).filter((word) => !stopWords.has(word));
}
