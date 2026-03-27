export const toClipboard = (value) => {
	navigator.clipboard.writeText(value)
}

export const getCurrencyIcon = (name) => {
	// Fallback to a generic icon or empty string if symbols-specific assets are gone
	try {
		return new URL(`../../assets/logo.png`, import.meta.url).href
	} catch (e) {
		return ""
	}
}

export const capitalizeFirstLetter = (str) => {
	return str.charAt(0).toUpperCase() + str.slice(1)
}

export const pluralize = (val, word, plural = word + "s") => {
	const _pluralize = (num, word, plural = word + "s") =>
		[1, -1].includes(Number(num)) ? word : plural
	if (typeof val === "object")
		return (num, word) => _pluralize(num, word, val[word])
	return _pluralize(val, word, plural)
}

export const shorten = (str, left = 6, right = 4) => {
  if (!str) return ""
	return `${str.slice(0, left)}...${str.slice(
		str.length - right,
		str.length,
	)}`
}

export const sanitizeInput = (e) => {
	if (["-", "e", "E"].includes(e.key)) e.preventDefault()
}

export const parsePoolName = (name) => {
	if (!name) return "Unknown"
	const parts = name.split("-")
	if (parts.length !== 3) return name
	const [base, quote, duration] = parts
	return `${base}/${quote} ${duration}`
}
