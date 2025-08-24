import httpx

DEFAULT_HTTP_PORT = 80
DEFAULT_USERNAME = ""
DEFAULT_PASSWORD = ""


# https://docs.homeseer.com/hspi/json-api
class Homeseer:
    """
    An object for interacting with the Homeseer HTTP JSON API.
    """

    def __init__(
        self,
        host: str,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        http_port: int = DEFAULT_HTTP_PORT,
    ) -> None:

        self._host = host
        self._http_port = http_port
        self._username = username
        self._password = password

    @property
    def _url(self) -> str:
        return f"http://{self._host}:{self._http_port}/JSON"

    def _request_url(self, action: str) -> str:
        return f"{self._url}?request={action}"

    async def invoke(self, url: str):
        """
        Invoke the Homeseer API.

        Returns the response from the Homeseer API.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        return None

    async def get_locations(self):
        """
        Get all locations from the Homeseer API.

        Returns all the location names for location 1 and location 2
        """
        url = self._request_url("getlocations")
        return await self.invoke(url)

    async def get_status(self,
                         ref=None,
                         location1=None,
                         location2=None,
                         compress=False,
                         everything=False,
                         ):
        """
        Get status from the Homeseer API.

        location1=loc1  (only return the devices that are in the specific location1, 
        omit or set to "all" for all devices at this location)

        location2=loc2  (only return the devices that are in the specific location2, 
        omit or set to "all" for all devices at this location)

        ref=##  (only return the device that matches the specific reference #, 
        this may be a list of reference #'s like 3467,2342,869, omit or set to 
        "all" to return all devices)

        compress=true (omit values that are not set, 
        greatly reduces the amount of data returned)

        compress=false (default setting, the FULL JSON is returned, even empty values)

        everything=false (default setting, returns only status information)        
        everything=true (returns status as well as control information for the requested devices)
            NOTE: everything supports the following queries only:
            - ref=list of comma seperated device refs
            - voiceonly
            - user
            - pass
        """

        url = self._request_url("getstatus")

        if ref:
            url += f"&ref={ref}"
        if location1:
            url += f"&location1={location1}"
        if location2:
            url += f"&location2={location2}"
        if compress:
            url += "&compress=true"
        if everything:
            url += "&everything=true"

        return await self.invoke(url)

    async def control_device_by_value(self, ref: int, value: int):
        """
        Control a device given the device's reference number "ref", and value "value". For example, if a light has a value of 0 for off, the following would turn off the device with reference # 3570:

        control_device_by_value(ref=3570, value=0)

        The return is the current JSON formatted status of the device (same return as "getstatus"), or the string "error".        

        ref=##  (the reference # of the device to control)

        value=##  (the value to set the device to)
        """
        url = self._request_url("controldevicebyvalue")
        url += f"&ref={ref}&value={value}"
        return await self.invoke(url)

    async def control_device_by_label(self, ref: int, label: str):
        """
        Control a device by label, this is the label as returned by the "getcontrol" parameter. 
        For example, if the device has a label "On" to turn a device on.

        The return is the current JSON formatted status of the device (same return as "getstatus"), or the string "error".        

        ref=##  (the reference # of the device to control)

        label=""  (the label to set the device to)
        """
        url = self._request_url("controldevicebylabel")
        url += f"&ref={ref}&label={label}"
        return await self.invoke(url)

    async def get_events(self):
        """
        Returns the names of all events in the system. An event is an action to be performed such as 
        controlling a light, a sequence of lights, a thermostat, etc. 
        Events have two properties, a group name and an event name. 
        This command returns the group name and event name for all events. 
        These two pieces of information are used to control an event.
        """
        url = self._request_url("getevents")
        return await self.invoke(url)

    async def get_control(self, ref: str):
        """
        Returns control information for a device in the system, or all devices. 
        Devices contain "control pairs", one pair for each possible control value. 
        For example, a light that can be turned on and off would contain 2 control pairs, 
        one for ON and one for OFF. The control pair describes how to control the device. 
        The most important information is the "Label" and the "ControlValue", 
        as those will be needed when the device is to be controlled. 
        The information from this call can be used to build 
        a user interface that will control the device.

        Parameters:

        ref=### (where ### is the device reference #, a list reference #'s, or "all" to return control information for all devices)
        """
        url = self._request_url("getcontrol2")
        url += f"&ref={ref}"
        return await self.invoke(url)
