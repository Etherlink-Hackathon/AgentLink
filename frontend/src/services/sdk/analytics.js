import amp from "amplitude-js"
import { currentNetwork } from "./flameWager"

const amplitude = amp.getInstance()

const log = (event, properties) => {
    amplitude.logEvent(event, { ...properties, network: currentNetwork.value })
}

export default { log }
