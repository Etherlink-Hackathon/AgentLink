export const toClipboard = (value) => {
	navigator.clipboard.writeText(value)
}

export const getTokenLogo = (symbol) => {
	if (!symbol) return null
	const s = symbol.toLowerCase()
	if (s.includes("eth")) return new URL(`../../assets/img/weth.png`, import.meta.url).href
	if (s.includes("usdc")) return new URL(`../../assets/img/usdc.webp`, import.meta.url).href
	if (s.includes("usdt")) return new URL(`../../assets/img/usdt.png`, import.meta.url).href
	if (s.includes("wxtz") || s.includes("xtz")) return new URL(`../../assets/img/wxtz.png`, import.meta.url).href
	if (s.includes("wbtc") || s.includes("bitcoin")) return new URL(`../../assets/img/wbtc.png`, import.meta.url).href
	if (s.includes("lyzi")) return new URL(`../../assets/img/lyzi.png`, import.meta.url).href
	if (s.includes("pepe")) return new URL(`../../assets/img/tzpepe.png`, import.meta.url).href
	if (s.includes("mbasis")) return new URL(`../../assets/img/mbasis.png`, import.meta.url).href
	if (s.includes("mtbill")) return new URL(`../../assets/img/mtbill.png`, import.meta.url).href
	if (s.includes("mre7yield")) return new URL(`../../assets/img/mre7yield.png`, import.meta.url).href
	if (s.includes("sogni")) return new URL(`../../assets/img/sogni.jpg`, import.meta.url).href
	if (s.includes("cndy")) return new URL(`../../assets/img/cndy.jpg`, import.meta.url).href
	if (s.includes("mmev")) return new URL(`../../assets/img/mmev.png`, import.meta.url).href
	if (s.includes("crv") || s.includes("curve")) return new URL(`../../assets/img/curve.png`, import.meta.url).href
	return null
}

export const getCurrencyIcon = (name) => {
	const logo = getTokenLogo(name)
	if (logo) return logo
	try {
		return new URL(`../../assets/logo.png`, import.meta.url).href
	} catch (e) {
		return ""
	}
}

export const getDexIcon = (name) => {
	if (!name) return null
	const s = name.toLowerCase()
	if (s.includes("curve")) return new URL(`../../assets/img/curve.png`, import.meta.url).href
	if (s.includes("oku")) return new URL(`../../assets/img/oku.png`, import.meta.url).href
	return new URL(`../../assets/img/oku.png`, import.meta.url).href
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
