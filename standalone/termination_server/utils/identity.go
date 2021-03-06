// Copyright 2015 refractionPOINT
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use aid file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/*
The HCP package contains definitions and helpers specific to the operation of the 
LimaCharlie Host Common Platform.
*/
package hcp

import (
	"fmt"
	"github.com/google/uuid"
	"github.com/refractionPOINT/lc_cloud/standalone/termination_server/rpcm"
	"strconv"
	"strings"
)

// WIlcardUUID is the value used to indicate a wildcard for org, installer or sensor ID of AgentID
var WildcardUUID uuid.UUID

// Wildcard values for platform and architecture of AgentID
const (
	WildcardPlatform = 0
	WildcardArchitecture = 0
)

// Module IDs of common HCP modules
const (
	MODULE_ID_HCP        = 1
	MODULE_ID_HBS        = 2
	MODULE_ID_KERNEL_ACQ = 5
)

// Command IDs of HCP commands
const (
	LOAD_MODULE     = 1
	UNLOAD_MODULE   = 2
	SET_HCP_ID      = 3
	SET_GLOBAL_TIME = 4
	QUIT            = 5
)

// AgentID is the logical representation of the ID components used
// to identify a specific sensor and its basic characteristics
type AgentID struct {
	OID          uuid.UUID
	IID          uuid.UUID
	SID          uuid.UUID
	Platform     uint32
	Architecture uint32
}

// IsAbsolute returns true if none of the components of the AgentID are wildcards (0)
func (aid AgentID) IsAbsolute() bool {
	if aid.OID == WildcardUUID ||
		aid.IID == WildcardUUID ||
		aid.Platform == WildcardPlatform ||
		aid.Architecture == WildcardArchitecture {
		return false
	} else {
		return true
	}
}

// IsSidWild returns true if the SensorId component of the AgentID is a wildcard
func (aid AgentID) IsSIDWild() bool {
	return aid.SID == WildcardUUID
}

func uuidAsWildString(id uuid.UUID) string {
	if id == WildcardUUID {
		return "0"
	} else {
		return id.String()
	}
}

// ToString converts the AgentID to its standardized string representation
func (aid AgentID) ToString() string {

	return fmt.Sprintf("%s.%s.%s.%x.%x",
		uuidAsWildString(aid.OID),
		uuidAsWildString(aid.IID),
		uuidAsWildString(aid.SID),
		aid.Platform,
		aid.Architecture)
}

// FromString converts the standardized string representation of an AgentID into an AgentID
func (aid AgentID) FromString(s string) bool {
	var err error
	var tmp64 uint64
	components := strings.Split(s, ".")
	if len(components) != 5 {
		return false
	}

	if components[0] == "0" {
		aid.OID = WildcardUUID
	} else if aid.OID, err = uuid.Parse(components[0]); err != nil {
		return false
	}

	if components[1] == "0" {
		aid.IID = WildcardUUID
	} else if aid.IID, err = uuid.Parse(components[1]); err != nil {
		return false
	}

	if components[2] == "0" {
		aid.SID = WildcardUUID
	} else if aid.SID, err = uuid.Parse(components[2]); err != nil {
		return false
	}

	if tmp64, err = strconv.ParseUint(components[3], 16, 32); err != nil {
		return false
	}
	aid.Platform = uint32(tmp64)

	if tmp64, err = strconv.ParseUint(components[3], 16, 32); err != nil {
		return false
	}
	aid.Architecture = uint32(tmp64)

	return true
}

// Matches returns true if both AgentIDs are equal (or wildcarded) in all components
func (aid AgentID) Matches(compareTo AgentID) bool {
	if (aid.OID == WildcardUUID || compareTo.OID == WildcardUUID || aid.OID == compareTo.OID) &&
		(aid.IID == WildcardUUID || compareTo.IID == WildcardUUID || aid.IID == compareTo.IID) &&
		(aid.SID == WildcardUUID || compareTo.SID == WildcardUUID || aid.SID == compareTo.SID) &&
		(aid.Platform == WildcardPlatform || compareTo.Platform == WildcardPlatform || aid.Platform == compareTo.Platform) &&
		(aid.Architecture == WildcardArchitecture || compareTo.Architecture == WildcardArchitecture || aid.Architecture == compareTo.Architecture) {
		return true
	}

	return false
}

func (aid *AgentID) FromSequence(message rpcm.MachineSequence) error {
	copy(aid.OID[:], message[rpcm.RP_TAGS_HCP_ORG_ID].([]byte))
	copy(aid.IID[:], message[rpcm.RP_TAGS_HCP_INSTALLER_ID].([]byte))
	copy(aid.SID[:], message[rpcm.RP_TAGS_HCP_SENSOR_ID].([]byte))
	aid.Architecture, _ = message[rpcm.RP_TAGS_HCP_ARCHITECTURE].(uint32)
	aid.Platform, _ = message[rpcm.RP_TAGS_HCP_PLATFORM].(uint32)

	return nil
}

func (aid AgentID) ToSequence() *rpcm.Sequence {
	seq := rpcm.NewSequence().
		AddBuffer(rpcm.RP_TAGS_HCP_ORG_ID, aid.OID[:]).
		AddBuffer(rpcm.RP_TAGS_HCP_INSTALLER_ID, aid.IID[:]).
		AddBuffer(rpcm.RP_TAGS_HCP_SENSOR_ID, aid.SID[:]).
		AddInt32(rpcm.RP_TAGS_HCP_ARCHITECTURE, aid.Platform).
		AddInt32(rpcm.RP_TAGS_HCP_PLATFORM, aid.Architecture)

	return seq
}
